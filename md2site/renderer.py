import re
from mistletoe import Document
from mistletoe import span_token

from mistletoe.html_renderer import HTMLRenderer
from mistletoe.span_token import RawText, SpanToken

from md2site.site import Site
from mistletoe.token import Token


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
    def __init__(self, config: Site):
        super().__init__(WikiLink)
        self.site = config

    def render_wiki_link(self, token: WikiLink):
        template = '<a href="{base_url}/{target}.html">{inner}</a>'
        target = self.site.link_map.get(token.target, "#")
        inner = self.render_inner(token)
        return template.format(base_url=self.site.base_url, target=target, inner=inner)


class Parser:
    def __init__(self):
        span_token.add_token(WikiLink)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_val, traceback):
        span_token.reset_tokens()

    def parse(self, markdown: str):
        document = Document(markdown)
        return document


def extract_wikilinks(markdown: str) -> set[str]:
    with Parser() as p:
        ast = p.parse(markdown)
        links = set()
        nodes: list[Token] = [ast]
        while nodes:
            node = nodes.pop(0)
            if isinstance(node, WikiLink):
                links.add(node.target)
            if isinstance(node, RawText):
                continue
            if hasattr(node, "children"):
                for child in node.children:
                    nodes.append(child)
        return links
