from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TextIO
import os

import yaml


@dataclass
class MarkdownContent:
    frontmatter: dict[str, str]
    body: str


@dataclass
class Post:
    """
    All information necessary to render a post.
    """

    title: str
    content: str
    summary: str
    created_at: datetime
    slug: str
    backlinks: list[str] = list()

    @classmethod
    def from_file(cls, filepath: Path) -> Post:
        with open(filepath, "r", encoding="utf-8") as f:
            content = separate_frontmatter(f)
            name = filepath.stem
            created_at = datetime.fromtimestamp(os.path.getctime(filepath))
            return Post(
                title=name,
                content=content.body,
                summary=content.body[:140],
                created_at=created_at,
                slug=name_to_slug(name),
            )


def parse_frontmatter(yaml_text: str) -> dict[str, str]:
    return yaml.safe_load(yaml_text)


def separate_frontmatter(markdown: TextIO) -> MarkdownContent:
    is_frontmatter = False
    frontmatter_lines: list[str] = []
    body_lines: list[str] = []
    for line_number, line in enumerate(markdown):
        if line_number == 0 and line == "---":
            continue
        if is_frontmatter and line == "---":
            is_frontmatter = False
            continue
        if is_frontmatter:
            frontmatter_lines.append(line)
        else:
            body_lines.append(line)

    frontmatter = parse_frontmatter("".join(frontmatter_lines))
    body = "".join(body_lines)
    return MarkdownContent(frontmatter, body)


def name_to_slug(name: str) -> str:
    return name.lower().replace(" ", "-")
