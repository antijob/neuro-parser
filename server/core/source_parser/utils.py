# Some functions that used across different modules
from typing import Union
from urllib.parse import urlparse, urljoin

from lxml.html.clean import Cleaner
from selectolax.parser import HTMLParser


CLEANER = Cleaner(
    scripts=True,
    javascript=True,
    comments=True,
    style=True,
    links=True,
    meta=True,
    add_nofollow=False,
    page_structure=True,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=True,
    annoying_tags=True,
    kill_tags=["img", "noscript", "button"],
    remove_unknown_tags=True,
    safe_attrs_only=False,
)


def count_links(node) -> int:
    count = 0
    for subnode in node:
        if subnode.tag == "a":
            count += 1
        else:
            count += count_links(subnode)
    return count


def remove_double_spaces(text: str) -> str:
    text = text.lstrip()
    while "  " in text:
        text = text.replace("  ", " ")
    while " \n" in text:
        text = text.replace(" \n", "\n")
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text


def is_correct_article_link(url: str) -> bool:
    if not url:
        return False
    if not url.startswith("http"):
        return False
    link_query = urlparse(url).query
    link_path = urlparse(url).path.strip("/")
    return link_path or link_query


def get_absolute_url(source_url: str, url: str) -> Union[str, None]:
    if not url:
        return None
    source_domain = urlparse(source_url).netloc
    link_domain = urlparse(url).netloc
    if not link_domain:
        link_domain = source_domain
        url = urljoin(source_url, url)
    if source_domain == link_domain:
        return url
    return None


def is_rss_link(url):
    path = str(urlparse(url).path)
    return "rss" in path or path.endswith(".xml") or "feed" in path


def build_document(html, clean=False):
    """
    Return etree document
    cleans it if clean = True
    """
    if not html:
        return None

    html.replace("\xa0", " ")

    if clean:
        html = CLEANER.clean_html(html)
    try:
        document = HTMLParser(html)
    except ValueError:
        pass

    return document
