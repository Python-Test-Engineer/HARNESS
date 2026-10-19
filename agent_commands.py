"""Load Markdown slash commands for the mini agent."""

from __future__ import annotations

import re
from pathlib import Path

COMMANDS_DIR = Path(__file__).resolve().parent / "commands"
_COMMAND_PREFIX = re.compile(r"\A/([A-Za-z0-9_-]+)(?=\s|$)")


def load_command(
    prompt: str, commands_dir: Path | None = None
) -> tuple[str, str] | None:
    """Read a matching commands/<NAME>.md file for a leading /NAME prompt."""
    match = _COMMAND_PREFIX.match(prompt)
    if not match:
        return None

    if commands_dir is None:
        commands_dir = COMMANDS_DIR
    requested_name = match.group(1).casefold()
    matches = [
        path
        for path in Path(commands_dir).glob("*.md")
        if path.stem.casefold() == requested_name
    ]
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f"Ambiguous command name: {match.group(1)}")

    command_path = matches[0]
    instructions = command_path.read_text(encoding="utf-8").strip()
    if not instructions:
        raise ValueError(f"Command file is empty: {command_path.name}")
    return command_path.stem, instructions


def format_size_report(
    prompt: str, usage: dict, context_window: int | None
) -> str:
    """Format raw user-prompt size and provider-reported context usage."""
    lines = [
        f"Prompt length: {len(prompt)} characters",
        f"Words: {len(prompt.split())}",
    ]

    prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
    total_tokens = usage.get("total_tokens") if isinstance(usage, dict) else None
    if isinstance(prompt_tokens, int) and not isinstance(prompt_tokens, bool):
        lines.append(f"Input tokens: {prompt_tokens}")
    else:
        lines.append("Input-token usage: unavailable")

    measured_tokens = total_tokens
    if not isinstance(measured_tokens, int) or isinstance(measured_tokens, bool):
        measured_tokens = prompt_tokens
    if (
        isinstance(measured_tokens, int)
        and not isinstance(measured_tokens, bool)
        and isinstance(context_window, int)
        and not isinstance(context_window, bool)
        and context_window > 0
    ):
        percentage = measured_tokens / context_window * 100
        lines.append(
            f"Tokens used: {measured_tokens} / {context_window} ({percentage:.2f}%)"
        )
    else:
        lines.append("Context-window usage: unavailable")

    lines.append(
        "Context usage uses the latest OpenRouter token-usage metadata and model context limit."
    )
    return "\n".join(lines)
