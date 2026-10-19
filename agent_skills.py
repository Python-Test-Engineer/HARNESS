"""Discover and load Markdown skills with YAML frontmatter."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).resolve().parent / "skills"
_FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---[ \t]*\r?\n(.*)\Z", re.DOTALL)
_SKILL_NAME = re.compile(r"\A[a-z0-9][a-z0-9_-]*\Z")


def _parse_skill(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"Invalid YAML frontmatter in {path.name}.")

    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict):
        raise ValueError(f"Skill frontmatter must be a YAML mapping in {path.name}.")

    name = metadata.get("name")
    description = metadata.get("description")
    body = match.group(2).strip()
    if not isinstance(name, str) or not _SKILL_NAME.fullmatch(name):
        raise ValueError(f"Invalid skill name in {path.name}.")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"Missing skill description in {path.name}.")
    if not body:
        raise ValueError(f"Missing skill instructions in {path.name}.")

    return {"name": name, "description": description.strip()}, body


def _skills(skills_dir: Path) -> list[tuple[dict[str, str], str]]:
    skills = []
    names = set()
    for path in sorted(skills_dir.glob("*.md"), key=lambda item: item.name.casefold()):
        metadata, body = _parse_skill(path)
        if metadata["name"] in names:
            raise ValueError(f"Duplicate skill name: {metadata['name']}")
        names.add(metadata["name"])
        skills.append((metadata, body))
    return skills


def discover_skills(skills_dir: Path = SKILLS_DIR) -> list[dict[str, str]]:
    """Return skill names and descriptions in deterministic order."""
    return [metadata for metadata, _ in _skills(Path(skills_dir))]


def read_skill(name: str, skills_dir: Path = SKILLS_DIR) -> str:
    """Return instructions for a discovered skill; reject unknown names."""
    for metadata, body in _skills(Path(skills_dir)):
        if metadata["name"] == name:
            return body
    raise ValueError(f"Unknown skill: {name}")


def skill_catalog_prompt(skills_dir: Path = SKILLS_DIR) -> str:
    """Format skill descriptions for the model's skill-selection prompt."""
    skills = discover_skills(skills_dir)
    if not skills:
        return "(no skills available)"
    return "\n".join(f"- {skill['name']}: {skill['description']}" for skill in skills)
