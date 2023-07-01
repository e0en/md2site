from pathlib import Path
import shutil

import jinja2
import toml

from md2site.post import Post
from md2site.site import Site

from md2site.renderer import Parser, Renderer, extract_wikilinks


def load_config() -> Site:
    raw_config = toml.load("config.toml")
    name = raw_config["name"]
    base_url = raw_config["base_url"]
    return Site(base_url, name)


def parse_markdown(markdown: str) -> str:
    return markdown


def load_post_files() -> list[Post]:
    posts = list()
    for child in Path("posts").iterdir():
        if child.name.endswith(".md"):
            posts.append(Post.from_file(child))
    return posts


def write_html(site: Site, post: Post, template: jinja2.Template):
    with open(f"dist/{post.slug}.html", "w", encoding="utf-8") as file:
        html = template.render(post=post, site=site)
        file.write(html)


def build_posts(posts: list[Post], site: Site):
    loader = jinja2.FileSystemLoader("template")
    env = jinja2.Environment(loader=loader)
    post_template = env.get_template("post.html")
    renderer = Renderer(site)
    parser = Parser()
    for post in posts:
        parsed = parser.parse(post.content)
        post.content = renderer.render(parsed)
        write_html(site, post, post_template)


def build_backlink_map(posts: list[Post]) -> dict[str, set[str]]:
    result = {}
    for p in posts:
        links = extract_wikilinks(p.content)
        for link in links:
            if link not in result:
                result[link] = set()
            result[link].add(p.title)
    return result


def build_link_map(posts: list[Post]) -> dict[str, str]:
    mapping = {}
    for post in posts:
        mapping[post.title] = post.slug
    return mapping


def copy_static_files():
    """
    copy every non-html file inside template/ folder to dist/.
    """
    output_folder = Path("./dist")
    for file in Path("./template").iterdir():
        if file.name.endswith(".html"):
            continue
        shutil.copyfile(file, output_folder / file.name)


def generate():
    copy_static_files()
    site = load_config()
    posts = load_post_files()
    site.link_map = build_link_map(posts)
    build_backlink_map(posts)
    build_posts(posts, site)
