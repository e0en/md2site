from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PostMetaData:
    name: str
    title: str
    created_at: datetime
    url: str


@dataclass
class Site:
    """
    Site configuration loaded from config.toml.
    """

    base_url: str
    name: str
    link_map: dict[str, str] = field(default_factory=dict)
    recent_posts: list[PostMetaData] = field(default_factory=list)
