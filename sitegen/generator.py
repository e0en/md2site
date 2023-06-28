import jinja2


def load_config() -> dict[str, str]:
    return {}


def load_all_posts() -> list[dict[str, str]]:
    return []


def write_html(html: str):
    pass


def generate():
    config = load_config()
    site = config["site"]
    env = jinja2.Environment()
    posts = load_all_posts()
    for post in posts:
        post_template = env.get_template("post.html")
        page = post_template.render(site, post)
        write_html(page)

    template = env.get_template("index.html")
    index_page = template.render(site)
    write_html(index_page)
