from pathlib import Path

import jinja2
import toml

from sitegen.post import Post
from sitegen.site import Site


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


def write_html(config: Site, post: Post, template: jinja2.Template):
    with open(f"dist/{post.slug}.html", "w", encoding="utf-8") as file:
        html = template.render(post=post, site=config)
        file.write(html)


def generate():
    config = load_config()
    env = jinja2.Environment()
    posts = load_post_files()
    post_template = env.get_template("post.html")
    for post in posts:
        write_html(config, post, post_template)
