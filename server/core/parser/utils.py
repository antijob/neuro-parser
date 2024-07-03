# Some functions that used across different modules
import dateparser
from datetime import datetime
from typing import Union
from urllib.parse import urlparse, urljoin, unquote
import re


def get_first_sentence(text: str) -> str:
    """
    Extracts the first sentence from given text
    """
    pattern = r"^[^.!?]+[.!?]"
    match = re.search(pattern, text)

    return match.group(0) if match else ""


# ToDo: fix Invalid date format: только что
def convert_date_format(date_string: str) -> str:
    """
    Parse data string and return in format %Y-%m-%d
    """
    current_date = datetime.now().strftime("%Y-%m-%d")

    if not date_string:
        return current_date

    date_obj = dateparser.parse(
        date_string, languages=["en", "ru"], settings={"TIMEZONE": "UTC"}
    )
    if date_obj:
        utc_date = date_obj.strftime("%Y-%m-%d")
        return utc_date
    else:
        print(f"Invalid date format: {date_string}")
        return current_date


def count_links(node) -> int:
    count = 0
    for subnode in node:
        if subnode.tag == "a":
            count += 1
        else:
            count += count_links(subnode)
    return count


def unquote_urls(urls):
    return set(unquote(url) for url in urls if url)


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
