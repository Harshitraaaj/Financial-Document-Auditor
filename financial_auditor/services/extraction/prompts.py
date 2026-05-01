from __future__ import annotations

from pathlib import Path


def load_prompt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_prompt(template: str, **values: str) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered

