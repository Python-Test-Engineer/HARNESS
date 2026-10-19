"""Tool implementations and OpenAI-compatible schemas for the agent."""

from __future__ import annotations

import subprocess
from pathlib import Path

WORKDIR = Path("work")
WORKDIR.mkdir(exist_ok=True)


def write_file(path: str, content: str) -> str:
    (WORKDIR / path).write_text(content)
    return f"Created {path}"


def edit_file(path: str, old: str, new: str) -> str:
    file_path = WORKDIR / path
    file_path.write_text(file_path.read_text().replace(old, new, 1))
    return f"Edited {path}: {old!r} -> {new!r}"


def read_file(path: str) -> str:
    return (WORKDIR / path).read_text()


def list_files(path: str = ".") -> str:
    work_root = WORKDIR.resolve()
    directory = (WORKDIR / path).resolve()
    if not directory.is_relative_to(work_root):
        raise ValueError("Path must stay inside the work directory.")
    entries = sorted(directory.iterdir(), key=lambda entry: entry.name.casefold())
    if not entries:
        return "(empty directory)"
    return "\n".join(
        f"{entry.name}/" if entry.is_dir() else entry.name for entry in entries
    )


def run(command: str) -> str:
    out = subprocess.run(
        command, shell=True, capture_output=True, text=True, cwd=WORKDIR
    )
    return out.stdout.strip() or out.stderr.strip()


TOOLS = {
    "write_file": write_file,
    "edit_file": edit_file,
    "read_file": read_file,
    "list_files": list_files,
    "run": run,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file in the work dir.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace the first occurrence of old with new in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old": {"type": "string"},
                    "new": {"type": "string"},
                },
                "required": ["path", "old", "new"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file in the work dir.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and subdirectories in a directory in the work dir. Defaults to the work dir.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run",
            "description": "Run a shell command in the work dir (e.g. 'python hello.py').",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
        },
    },
]
