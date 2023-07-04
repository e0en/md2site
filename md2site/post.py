from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO
import os

import yaml

from md2site.site import PostMetaData


@dataclass
class MarkdownContent:
    frontmatter: dict[str, str]
    body: str


@dataclass
class Post:
    """
    All information necessary to render a post.
    """

    name: str
    title: str
    content: str
    summary: str
    created_at: datetime
    slug: str
    prev_post: PostMetaData | None = None
    next_post: PostMetaData | None = None
    backlinks: list[str] = field(default_factory=list)

    @classmethod
    def from_file(cls, filepath: Path) -> Post:
        with open(filepath, "r", encoding="utf-8") as f:
            content = separate_frontmatter(f)
            name = filepath.stem
            if "title" in content.frontmatter:
                title = content.frontmatter["title"]
            else:
                title = name

            if "date" in content.frontmatter:
                created_at = content.frontmatter["date"]
            else:
                created_at = datetime.fromtimestamp(os.path.getctime(filepath)).replace(
                    tzinfo=timezone.utc
                )
            return Post(
                name=name,
                title=title,
                content=content.body,
                summary=content.body[:140],
                created_at=created_at,
                slug=name_to_slug(name),
            )


def parse_frontmatter(yaml_text: str) -> dict[str, str]:
    parsed = yaml.safe_load(yaml_text)
    if parsed is not None:
        return parsed
    else:
        return {}


def separate_frontmatter(markdown: TextIO) -> MarkdownContent:
    is_frontmatter = False
    frontmatter_lines: list[str] = []
    body_lines: list[str] = []
    for line_number, line in enumerate(markdown):
        if line_number == 0 and line.strip() == "---":
            is_frontmatter = True
            continue
        if is_frontmatter and line.strip() == "---":
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
