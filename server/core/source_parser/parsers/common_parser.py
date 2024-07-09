from typing import Iterable

from urllib.parse import urlparse
from lxml import cssselect, etree

from server.core.article_parser.parsers.base_parser import ParserBase
from ..utils import (
    is_correct_article_link,
    get_absolute_url,
    is_rss_link,
    remove_double_spaces,
    count_links,
)

MIN_WORDS_IN_SENTENCE = 5
TAGS_WITHOUT_CONTENT = ["form", "select", "input", "textarea", "button"]
BLOCK_TAGS = [
    "address",
    "article",
    "aside",
    "blockquote",
    "canvas",
    "dd",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "li",
    "main",
    "nav",
    "ol",
    "p",
    "pre",
    "section",
    "table",
    "tfoot",
    "ul",
]
IGNORED_IDS = ["comments_block", "seo"]
IGNORED_CLASSES = [
    "print-data",
    "alert-warning",
    "breadcrumb-list",
    "feeds-page__header",
    "feeds-page__navigation",
    "feeds-page__title",
    "button",
    "btn",
    "subscribe__popover_field",
    "news_image",
    "donate_text",
    "img",
    "social-block",
    "news_date",
    "crumb",
    "svg",
    "twitter-share-button",
    "rpbt_shortcode",
    "tags",
    "overtitle",
    "date-and-region",
    "main-thematic",
    "related-gallery",
    "mz-publish__sidebar",
    "mz-layout-content__col-main",
]
ACCEPTABLE_EXTENSIONS = ["htm", "html", "shtml", "php", "asp", "jsp"]
SERVICE_TAGS = ["script", "style", "head", "aside"]
IGNORED_PATHS = [
    "about",
    "stat",
    "statistics",
    "statistika",
    "statisticheskie-dannyie",
    "contacts",
    "kontakty",
    "search",
    "feedback",
    "internet-priemnaya",
    "priemnaya",
    "reception",
    "icenter",
    "for-people",
    "housing",
    "internet-and-reception",
    "structure",
    "struktura",
    "staff",
    "kadry",
    "kadrovoe-obespechenie",
    "management",
    "guide",
    "job",
    "vacancy",
    "recruit",
    "priem-na-sluzhbu",
    "vacancies",
    "sitemap",
    "map_site",
    "help",
    "faq",
    "links",
    "karta-sajta",
    "pda",
    "documents",
    "docs",
    "dokumenty",
    "mailing",
    "for-mass-media",
    "video",
    "video_soc",
    "audio",
    "photo",
    "media",
    "gallery",
    "photogallery",
    "fotogalereya",
    "goods",
    "zakupki",
    "goszakupki",
    "zakaz",
    "gosudarstvennye-zakupki",
    "purchases",
    "contests",
    "citizens",
    "priem-grazhdan",
    "peopleware",
    "predprinimatelyam",
    "poryadok-obrashheniya-grazhdan",
    "uvedomlenie-ob-ekstremizme",
    "uvedomleniya-ob-ekstremizme",
    "borba-s-ekstremizmom",
    "extremism",
    "antiterror",
    "prokuratura-razyasnyaet",
    "explain",
    "pravovoe-prosveshhenie",
    "zapros-ot-smi",
    "rules",
    "plan",
    "k-svedeniyu-smi",
    "press-sluzhba",
    "k-svedeniyu",
    "vzaimodeystvie-so-smi",
    "mass-communications",
    "nurnberg",
    "nyurnbergskiy-process",
    "history",
    "istoriya",
    "veteran",
    "sovet-veteranov",
    "veterans",
    "against",
    "verify",
    "colleg",
    "control",
    "projects",
    "attention",
    "service",
    "references",
    "folder",
    "law_info",
    "anti_corruption",
    "corruption",
    "anticor",
    "borba-s-korrupcziej",
    "protivodejstvie-korruptsii",
    "anticorruption",
    "finance",
    "anti-corruption",
    "antinar",
    "antinark",
    "tender",
    "regions",
    "prosecutors-offices-of-region",
    "acts",
    "anounce",
    "anounces",
    "programma-territoriya-zakona",
    "usloviya-ispolzovaniya-sayta",
    "sluzhba",
    "oficialnyy-banner",
    "requirements",
    "education",
    "coordination",
    "o-razrabotke-sayta",
    "usloviya-ispolzovaniya-sayta",
    "audit",
    "government-service",
    "chamber-of-commerce",
]


def is_path_ignored(url: str) -> bool:
    path = str(urlparse(url).path)
    splitted = path.rsplit(".", maxsplit=1)

    if len(splitted) > 1:
        if splitted[-1] not in ACCEPTABLE_EXTENSIONS:
            return True
        path = splitted[0]
    splitted_path = path.split("/")
    if "news" in splitted_path:
        return False
    for ignored in IGNORED_PATHS:
        if ignored in splitted_path:
            return True


def is_valid_link_text(link_text):
    too_short = len(link_text.split()) < MIN_WORDS_IN_SENTENCE
    if not too_short:
        return True
    if (
        "подробнее" in link_text.lower()
        or "читать полностью" in link_text.lower()
        or "читать далее" in link_text.lower()
    ):
        return True
    return False


def is_inside_service_tag(node) -> bool:
    while True:
        parent = node.getparent()
        if parent is None:
            return False
        if parent.tag in SERVICE_TAGS:
            return True
        node = parent


def children_text_content(node, long_text_only: bool, include_links: bool) -> str:
    if node is None:
        return ""

    klass = node.get("class", "")
    if "menu" in klass or "footer" in klass:
        return ""

    texts = []
    for child in node:
        if child.tag != "h1":
            content = text_content(child, long_text_only, include_links)
            if content:
                texts += [content]
            else:
                child.getparent().remove(child)
    return "\n".join(texts)


def text_content(node, long_text_only: bool = False, include_links: bool = True) -> str:
    """Returns text content of node and its children.
    Ignores headings and service tags."""
    if node is None:
        return ""
    if node.tag in SERVICE_TAGS:
        return ""
    if node.tag in TAGS_WITHOUT_CONTENT:
        return ""
    if node.tag is etree.Comment:
        return ""

    node_id = node.get("id")
    if node_id:
        for id_ in IGNORED_IDS:
            if id_ in node_id:
                return ""
    node_classes = node.get("class", "").split()
    if node_classes:
        for class_ in IGNORED_CLASSES:
            if class_ in node_classes:
                return ""

    if not include_links:
        dot_count = ((node.text or "") + (node.tail or "")).count(".")
        link_count = count_links(node)
        if link_count >= max(dot_count, 3):
            return ""

    # Concat node text and its children texts
    children_text = children_text_content(node, long_text_only, include_links)
    text = (node.text or "") + children_text + (node.tail or "")
    if long_text_only and len(text.split()) < MIN_WORDS_IN_SENTENCE:
        return ""
    if node.tag in BLOCK_TAGS:
        text += "\n\n"
    else:
        text += " "
    return remove_double_spaces(text)


class CommonParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return True  # Default parser

    @classmethod
    def extract_urls(cls, source_url: str, document) -> Iterable[str]:
        if document is None:
            return []
        links = cssselect.CSSSelector("a")(document)

        for link in links:
            if is_inside_service_tag(link):
                continue
            link_text = text_content(
                link, long_text_only=False, include_links=True
            ).strip()
            if not is_valid_link_text(link_text):
                continue
            url = get_absolute_url(source_url, link.get("href"))
            if not is_correct_article_link(url):
                continue
            if is_path_ignored(url):
                continue
            if not is_rss_link(url):
                yield url
