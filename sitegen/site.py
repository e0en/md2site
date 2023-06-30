from dataclasses import dataclass


@dataclass
class Site:
    """
    Site configuration loaded from config.toml.
    """

    base_url: str
    name: str
