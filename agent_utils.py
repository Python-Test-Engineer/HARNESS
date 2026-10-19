"""Configuration and OpenRouter chat utilities used by the agent."""

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

from agent_tools import TOOL_SCHEMAS


def _load_env_file() -> None:
    """Load simple KEY=VALUE settings without overriding the process env."""
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.is_file():
        return

    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        name, separator, value = line.partition("=")
        if not separator or not name.strip():
            continue
        name, value = name.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        os.environ.setdefault(name, value)


def _api_key() -> str:
    _load_env_file()
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    raise SystemExit("No OPENROUTER_API_KEY found (environment or project .env).")


def _model() -> str:
    _load_env_file()
    model = os.environ.get("MODEL")
    if model:
        return model
    return "deepseek/deepseek-v4.1-flash"


def model_context_length(model: str | None = None) -> int | None:
    """Look up a model's context limit from OpenRouter's public model catalog."""
    model_id = model or _model()
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/models",
        headers={"Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            catalog = json.loads(response.read())
    except (OSError, ValueError):
        return None

    models = catalog.get("data", []) if isinstance(catalog, dict) else []
    for entry in models:
        if isinstance(entry, dict) and entry.get("id", "").casefold() == model_id.casefold():
            context_length = entry.get("context_length")
            if isinstance(context_length, int) and not isinstance(context_length, bool):
                return context_length if context_length > 0 else None
    return None


def chat(messages: list[dict]) -> dict:
    body = json.dumps(
        {
            "model": _model(),
            "messages": messages,
            "tools": TOOL_SCHEMAS,
        }
    ).encode()
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {_api_key()}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())
