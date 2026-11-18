"""Build indexes and package a reproducible, public-only index bundle."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from corpus import DATA, read_baseline
from chunk import STRATEGIES
from model_api import RAGError
from settings import Settings, load_settings, save_library
from vector_store import (FORMAT_VERSION, LOCK, STATE_FILE, ensure_collections, index_path,
                          locate_index, open_store, read_index_state, update_indexes, verify_binding)

BUNDLE = DATA / "prebuilt-index.zip"


def make_bundle(settings: Settings, path: Path) -> dict:
    """Export committed public vectors from an existing index without API calls."""
    from qdrant_client import models

    docs, _, corpus_hash = read_baseline()
    public_ids = {doc["doc_id"] for doc in docs}
    source, state = locate_index(settings, corpus_hash)
    if not public_ids.issubset(state.get("documents", [])):
        raise RAGError("Build the public corpus for these embedding settings before exporting a bundle.")

    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=path.parent, prefix=".index-bundle-") as temporary:
        temporary = Path(temporary)
        snapshot = temporary / "source"
        export = temporary / "export"
        # Open only a copy of the working Qdrant store so bundling never mutates it.
        with LOCK:
            shutil.copytree(source / "qdrant", snapshot / "qdrant", ignore=shutil.ignore_patterns(".lock"))
        if read_index_state(source) != state:
            raise RAGError("The index changed during export. Try again after the update finishes.")

        public = models.Filter(must=[
            models.FieldCondition(key="doc_id", match=models.MatchAny(any=sorted(public_ids)))
        ])
        manifest = {"profile": state["profile"], "dimensions": state["dimensions"],
                    "documents": sorted(public_ids), "chunks": {}}
        with open_store(snapshot) as current, open_store(export) as target:
            ensure_collections(target, manifest["dimensions"])
            for strategy in STRATEGIES:
                offset = None
                seen = set()
                count = 0
                while True:
                    points, offset = current.scroll(collection_name=strategy, scroll_filter=public,
                                                    limit=128, offset=offset, with_vectors=True)
                    if points:
                        seen.update(point.payload["doc_id"] for point in points)
                        target.upsert(collection_name=strategy, points=[
                            models.PointStruct(id=point.id, vector=point.vector, payload=point.payload)
                            for point in points
                        ])
                        count += len(points)
                    if offset is None:
                        break
                if seen != public_ids:
                    raise RAGError(f"The {strategy} index is missing one or more public pages.")
                manifest["chunks"][strategy] = count
        (export / STATE_FILE).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        archive = temporary / "bundle.zip"
        with ZipFile(archive, "w", ZIP_DEFLATED) as output:
            for file in sorted(export.rglob("*")):
                if file.is_file() and file.name != ".lock":
                    output.write(file, file.relative_to(export).as_posix())
        archive.replace(path)
    return manifest


def bundle_manifest(path: Path = BUNDLE) -> dict:
    with ZipFile(path) as archive:
        return json.loads(archive.read(STATE_FILE))


def install_bundle(settings: Settings, path: Path = BUNDLE) -> dict:
    docs, _, corpus_hash = read_baseline()
    public_ids = {doc["doc_id"] for doc in docs}
    with ZipFile(path) as archive:
        state = json.loads(archive.read(STATE_FILE))
        profile = state["profile"]
        if profile.get("corpus") != corpus_hash or profile.get("format") != FORMAT_VERSION:
            raise RAGError("This bundle does not match the current corpus or index format.")
        if set(state["documents"]) != public_ids:
            raise RAGError("This bundle does not contain the expected public corpus.")
        destination = index_path(settings, profile)
        if destination.exists():
            installed = existing_bundle_state(destination, state)
            verify_binding(settings, destination, installed, public_ids)
            return {**installed, "library_id": destination.name}

        settings.store.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=settings.store) as temporary:
            staged = Path(temporary) / "profile"
            archive.extractall(staged)
            verify_binding(settings, staged, state, public_ids)
            with LOCK:
                if destination.exists():
                    state = existing_bundle_state(destination, state)
                else:
                    staged.rename(destination)
    return {**state, "library_id": destination.name}


def existing_bundle_state(destination: Path, manifest: dict) -> dict:
    state = read_index_state(destination)
    if (state.get("profile") != manifest["profile"] or state.get("dimensions") != manifest["dimensions"]
            or not set(manifest["documents"]).issubset(state.get("documents", []))):
        raise RAGError("An existing local library uses this ID. It was left intact.")
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "bundle", "install"))
    parser.add_argument("--archive", type=Path, default=BUNDLE)
    args = parser.parse_args()
    settings = load_settings()

    def progress(done: int, total: int) -> None:
        print(f"Embedded {done}/{total} unique chunks", end="\r", flush=True)

    try:
        if args.action == "bundle":
            state = make_bundle(settings, args.archive)
            print(f"\nBundle: {args.archive} ({args.archive.stat().st_size / 1024**2:.1f} MiB)")
        elif args.action == "install":
            state = install_bundle(settings, args.archive)
            save_library(settings, state["library_id"], "Preset pandas library")
        else:
            state = update_indexes(settings, progress=progress)
        print(f"\nIndexed {len(state['documents'])} pages at {state['dimensions']} dimensions.")
        print(json.dumps(state["chunks"]))
    except (OSError, ValueError, RAGError) as exc:
        parser.exit(1, f"\n{exc}\n")


if __name__ == "__main__":
    main()
