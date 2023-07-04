import os
from pathlib import Path
import shutil

import jinja2
import toml

from md2site.post import Post, name_to_slug
from md2site.site import PostMetaData, Site

from md2site.renderer import Parser, Renderer, extract_wikilinks


def prepare_output_folder():
    output_folder = Path("dist")
    if output_folder.exists():
        shutil.rmtree(output_folder, ignore_errors=True)
    os.makedirs(output_folder)


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
    posts.sort(key=lambda p: p.created_at, reverse=True)
    return posts


def write_html(site: Site, post: Post, template: jinja2.Template):
    with open(f"dist/{post.slug}.html", "w", encoding="utf-8") as file:
        html = template.render(post=post, site=site)
        file.write(html)


def build_posts(posts: list[Post], site: Site):
    loader = jinja2.FileSystemLoader("template")
    env = jinja2.Environment(loader=loader)
    post_template = env.get_template("post.html")
    index_template = env.get_template("index.html")
    renderer = Renderer(site)
    parser = Parser()
    for post in posts:
        parsed = parser.parse(post.content)
        post.content = renderer.render(parsed)
        if post.name == "index":
            write_html(site, post, index_template)
        else:
            write_html(site, post, post_template)


def populate_backlinks(posts: list[Post], base_url: str):
    backlink_map = build_backlink_map(posts)
    for post in posts:
        if post.name not in backlink_map:
            continue
        backlinks = []
        for name in backlink_map[post.name]:
            backlinks.append({"title": name, "url": name_to_url(name, base_url)})
        post.backlinks = backlinks


def name_to_url(name: str, base_url: str) -> str:
    return f"{base_url}/{name_to_slug(name)}.html"


def populate_prev_next_links(posts: list[Post], base_url: str):
    for index, post in enumerate(posts):
        if index > 0:
            prev_post = posts[index - 1]
            post.prev_post = PostMetaData(
                prev_post.name,
                prev_post.title,
                prev_post.created_at,
                name_to_url(prev_post.name, base_url),
            )
        if index < len(posts) - 1:
            next_post = posts[index + 1]
            post.next_post = PostMetaData(
                next_post.name,
                next_post.title,
                next_post.created_at,
                name_to_url(next_post.name, base_url),
            )


def build_backlink_map(posts: list[Post]) -> dict[str, set[str]]:
    result = {}
    for p in posts:
        links = extract_wikilinks(p.content)
        for link in links:
            if link not in result:
                result[link] = set()
            result[link].add(p.name)
    return result


def build_link_map(posts: list[Post]) -> dict[str, str]:
    mapping = {}
    for post in posts:
        mapping[post.name] = post.slug
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
    prepare_output_folder()
    copy_static_files()
    site = load_config()
    posts = load_post_files()
    site.link_map = build_link_map(posts)
    site.recent_posts = [
        PostMetaData(p.name, p.title, p.created_at, name_to_url(p.name, site.base_url))
        for p in posts[:10]
    ]
    populate_backlinks(posts, site.base_url)
    populate_prev_next_links(posts, site.base_url)
    build_posts(posts, site)
