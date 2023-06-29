from dataclasses import dataclass
from datetime import datetime


@dataclass
class Site:
    """
    Site configuration loaded from config.toml.
    """

    base_url: str
    name: str


@dataclass
class BackLink:
    """
    Defines location and content of a backlink in a markdown file.
    """

    start_index: int
    end_index: int
    page_title: str
    display_text: str


@dataclass
class Post:
    """
    All information necessary to render a post.
    """

    url: str
    title: str
    content: str
    created_at: datetime
    summary: str
    backlinks: list[BackLink]
