"""Run a cooperative indexing job outside the Streamlit request thread."""
from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from threading import Condition, Lock, Thread

from settings import Settings
from vector_store import update_indexes

ACTIVE = {"running", "pausing", "paused", "stopping"}


class IndexStopped(Exception):
    pass


@dataclass(frozen=True)
class IndexProgress:
    state: str = "running"
    stage: str = "prepare"
    done: int = 0
    total: int = 0
    error: str = ""


class IndexJob:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._changed = Condition()
        self._progress = IndexProgress()

    def snapshot(self) -> IndexProgress:
        with self._changed:
            return self._progress

    def matches(self, settings: Settings) -> bool:
        return (self._settings.library_id, self._settings.embedding.base_url,
                self._settings.embedding.model, self._settings.dimensions) == (
                    settings.library_id, settings.embedding.base_url, settings.embedding.model, settings.dimensions)

    def pause(self) -> None:
        self._change({"running"}, "pausing")

    def resume(self) -> None:
        self._change({"paused", "pausing"}, "running")

    def stop(self) -> None:
        self._change({"running", "pausing", "paused"}, "stopping")

    def _change(self, allowed: set[str], state: str) -> None:
        with self._changed:
            if self._progress.state in allowed and self._progress.stage != "publish":
                self._progress = replace(self._progress, state=state)
                self._changed.notify_all()

    def _checkpoint(self) -> None:
        with self._changed:
            if self._progress.state == "pausing":
                self._progress = replace(self._progress, state="paused")
            self._changed.wait_for(lambda: self._progress.state != "paused")
            if self._progress.state == "stopping":
                raise IndexStopped

    def _report(self, stage: str, done: int, total: int) -> None:
        with self._changed:
            if stage == "publish":
                self._checkpoint()
            self._progress = replace(self._progress, stage=stage, done=done, total=total)

    def run(self) -> None:
        try:
            update_indexes(self._settings, report=self._report, checkpoint=self._checkpoint)
        except IndexStopped:
            state, message = "stopped", ""
        except Exception as exc:
            state, message = "failed", str(exc)
        else:
            state, message = "complete", ""
        with self._changed:
            self._progress = replace(self._progress, state=state, error=message)


_jobs: dict[Path, IndexJob] = {}
_jobs_lock = Lock()


def get_job(settings: Settings) -> IndexJob | None:
    with _jobs_lock:
        job = _jobs.get(settings.store.resolve())
        if job and (job.snapshot().state in ACTIVE or job.matches(settings)):
            return job
        return None


def start_job(settings: Settings) -> None:
    with _jobs_lock:
        directory = settings.store.resolve()
        existing = _jobs.get(directory)
        if existing and existing.snapshot().state in ACTIVE:
            return
        job = _jobs[directory] = IndexJob(settings)
        Thread(target=job.run, daemon=True, name="pandas-indexer").start()
