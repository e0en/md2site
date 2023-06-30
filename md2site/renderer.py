import re

from mistletoe.html_renderer import HTMLRenderer
from mistletoe.span_token import RawText, SpanToken


class WikiLink(SpanToken):
    """
    Obsidian-style wiki link token.
    `[[page_name]]` or `[[page_name|link_text]]`.

    This is an inline token with a single child of type RawText.
    """

    pattern = re.compile(r"\[\[([\s\S]+?[\s\S]+?)\]\]")
    parse_inner = False

    def __init__(self, match: re.Match):
        super().__init__(match)
        self.target: str = ""
        link_text = match.group(1)
        splits = link_text.split("|", 1)
        self.target = splits[0].strip()
        if len(splits) == 1:
            self.children = (RawText(self.target),)
        else:
            self.children = (RawText(splits[1].strip()),)


class Renderer(HTMLRenderer):
    def __init__(self, base_url: str):
        super().__init__(WikiLink)
        self.base_url = base_url

    def render_wiki_link(self, token: WikiLink):
        template = '<a href="{base_url}/{target}">{inner}</a>'
        target = token.target
        inner = self.render_inner(token)
        return template.format(base_url=self.base_url, target=target, inner=inner)
