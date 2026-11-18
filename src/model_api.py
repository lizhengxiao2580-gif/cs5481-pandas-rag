"""Use the shared OpenAI-compatible subset for both model endpoints."""
from __future__ import annotations

import math
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from settings import Endpoint, Settings

if TYPE_CHECKING:
    from openai import APIError, OpenAI


class RAGError(RuntimeError):
    """An actionable failure safe to display in the UI."""


def endpoint_url(endpoint: Endpoint) -> str:
    address = endpoint.base_url.strip().rstrip("/")
    address = address.removesuffix("/embeddings").removesuffix("/chat/completions")
    try:
        parts = urlsplit(address)
        if (parts.scheme in {"http", "https"} and parts.hostname
                and not (parts.username or parts.password or parts.query or parts.fragment)):
            return address
    except ValueError:
        pass
    raise RAGError("Enter the API base URL, including its version path (for example /v1).")


def check_endpoint(endpoint: Endpoint, label: str) -> None:
    if not endpoint.base_url or not endpoint.model:
        raise RAGError(f"Configure the {label} base URL and model in Settings.")
    endpoint_url(endpoint)
    if not endpoint.key():
        raise RAGError(f"Set the API key for {label} in Settings or its environment variable.")


def client_for(endpoint: Endpoint) -> OpenAI:
    from openai import OpenAI

    return OpenAI(base_url=endpoint_url(endpoint), api_key=endpoint.key(), timeout=40, max_retries=2)


def embed(settings: Settings, texts: list[str], *, query: bool = False) -> list[list[float]]:
    from openai import APIError

    endpoint = settings.embedding
    check_endpoint(endpoint, "embedding")
    if query and settings.query_instruction:
        texts = [f"Instruct: {settings.query_instruction}\nQuery: {text}" for text in texts]
    options = {"dimensions": settings.dimensions} if settings.dimensions is not None else {}
    model_input = texts[0] if len(texts) == 1 else texts
    try:
        with client_for(endpoint) as client:
            response = client.embeddings.create(
                model=endpoint.model, input=model_input, encoding_format="float", **options,
            )
    except APIError as exc:
        raise RAGError(api_message("Embedding", exc)) from exc

    rows = sorted(response.data, key=lambda row: row.index)
    if [row.index for row in rows] != list(range(len(texts))):
        raise RAGError("Embedding API returned an unexpected number of vectors.")
    vectors = [row.embedding for row in rows]
    dimension = settings.dimensions or len(vectors[0])
    if not dimension or any(len(vector) != dimension or not all(map(math.isfinite, vector))
                            or not any(vector) for vector in vectors):
        raise RAGError("Embedding API returned invalid vectors or a different dimension.")
    return vectors


def complete(settings: Settings, messages: list[dict], *, probe: bool = False) -> str:
    from openai import APIError

    endpoint = settings.generation
    check_endpoint(endpoint, "generation")
    options = {}
    if settings.temperature is not None:
        options["temperature"] = settings.temperature
    if probe:
        options["max_tokens"] = 32
    elif settings.max_tokens is not None:
        options["max_tokens"] = settings.max_tokens
    try:
        with client_for(endpoint) as client:
            response = client.chat.completions.create(model=endpoint.model, messages=messages, **options)
    except APIError as exc:
        raise RAGError(api_message("Generation", exc)) from exc
    text = response.choices[0].message.content if response.choices else None
    if not text or not text.strip():
        raise RAGError("Generation API returned an empty answer.")
    return text.strip()


def api_message(label: str, error: APIError) -> str:
    status = getattr(error, "status_code", None)
    detail = {
        400: "check the model and request options",
        401: "check the API key",
        403: "check API key permissions for this model",
        404: "check the base URL and model ID",
        429: "rate limit or quota reached",
    }.get(status, "try again or check the provider status")
    return f"{label} API failed ({status or 'connection error'}): {detail}."
