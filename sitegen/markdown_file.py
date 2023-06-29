from dataclasses import dataclass
from io import StringIO

import yaml


@dataclass
class MarkdownDocument:
    frontmatter: dict[str, str]
    content: str


def parse_frontmatter(yaml_text: str) -> dict[str, str]:
    return yaml.safe_load(yaml_text)


def separate_frontmatter(markdown: StringIO) -> MarkdownDocument:
    is_frontmatter = False
    frontmatter_lines: list[str] = []
    content_lines: list[str] = []
    for line_number, line in enumerate(markdown):
        if line_number == 0 and line == "---":
            continue
        if is_frontmatter and line == "---":
            is_frontmatter = False
            continue
        if is_frontmatter:
            frontmatter_lines.append(line)
        else:
            content_lines.append(line)

    frontmatter = parse_frontmatter("".join(frontmatter_lines))
    content = "".join(content_lines)
    return MarkdownDocument(frontmatter, content)
