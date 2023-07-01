from dataclasses import dataclass, field


@dataclass
class Site:
    """
    Site configuration loaded from config.toml.
    """

    base_url: str
    name: str
    link_map: dict[str, str] = field(default_factory=dict)
