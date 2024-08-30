from typing import Iterable

from urllib.parse import urlparse

from .base_parser import ParserBase, Source
from ..utils import (
    is_correct_article_link,
    get_absolute_url,
    is_rss_link,
    build_document,
)

# fmt: off

MIN_WORDS_IN_SENTENCE = 5
TAGS_WITHOUT_CONTENT = ["form", "select", "input", "textarea", "button"]
BLOCK_TAGS = [
    "address", "article", "aside", "blockquote", "canvas", "dd", "div",
    "dl", "dt", "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "header", "li", "main", "nav",
    "ol", "p", "pre", "section", "table", "tfoot", "ul"
]
IGNORED_IDS = ["comments_block", "seo"]
IGNORED_CLASSES = [
    "print-data", "alert-warning", "breadcrumb-list", "feeds-page__header",
    "feeds-page__navigation", "feeds-page__title", "button", "btn",
    "subscribe__popover_field", "news_image", "donate_text", "img",
    "social-block", "news_date", "crumb", "svg", "twitter-share-button",
    "rpbt_shortcode", "tags", "overtitle", "date-and-region",
    "main-thematic", "related-gallery", "mz-publish__sidebar",
    "mz-layout-content__col-main"
]
ACCEPTABLE_EXTENSIONS = ["htm", "html", "shtml", "php", "asp", "jsp"]
SERVICE_TAGS = ["script", "style", "head", "aside"]
IGNORED_PATHS = [
    "about", "stat", "statistics", "statistika", "statisticheskie-dannyie",
    "contacts", "kontakty", "search", "feedback", "internet-priemnaya",
    "priemnaya", "reception", "icenter", "for-people", "housing",
    "internet-and-reception", "structure", "struktura", "staff", "kadry",
    "kadrovoe-obespechenie", "management", "guide", "job", "vacancy",
    "recruit", "priem-na-sluzhbu", "vacancies", "sitemap", "map_site",
    "help", "faq", "links", "karta-sajta", "pda", "documents", "docs",
    "dokumenty", "mailing", "for-mass-media", "video", "video_soc",
    "audio", "photo", "media", "gallery", "photogallery", "fotogalereya",
    "goods", "zakupki", "goszakupki", "zakaz", "gosudarstvennye-zakupki",
    "purchases", "contests", "citizens", "priem-grazhdan", "peopleware",
    "predprinimatelyam", "poryadok-obrashheniya-grazhdan",
    "uvedomlenie-ob-ekstremizme", "uvedomleniya-ob-ekstremizme",
    "borba-s-ekstremizmom", "extremism", "antiterror",
    "prokuratura-razyasnyaet", "explain", "pravovoe-prosveshhenie",
    "zapros-ot-smi", "rules", "plan", "k-svedeniyu-smi", "press-sluzhba",
    "k-svedeniyu", "vzaimodeystvie-so-smi", "mass-communications",
    "nurnberg", "nyurnbergskiy-process", "history", "istoriya", "veteran",
    "sovet-veteranov", "veterans", "against", "verify", "colleg", "control",
    "projects", "attention", "service", "references", "folder", "law_info",
    "anti_corruption", "corruption", "anticor", "borba-s-korrupcziej",
    "protivodejstvie-korruptsii", "anticorruption", "finance",
    "anti-corruption", "antinar", "antinark", "tender", "regions",
    "prosecutors-offices-of-region", "acts", "anounce", "anounces",
    "programma-territoriya-zakona", "usloviya-ispolzovaniya-sayta",
    "sluzhba", "oficialnyy-banner", "requirements", "education",
    "coordination", "o-razrabotke-sayta", "usloviya-ispolzovaniya-sayta",
    "audit", "government-service", "chamber-of-commerce"
]

# fmt: on


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


def recursive_delete(node):
    if (
        node.id
        and node.id in IGNORED_IDS
        or "class" in node.attrs
        and node.attrs["class"] in IGNORED_CLASSES
    ):
        node.decompose()
        return

    for child in node.iter():
        recursive_delete(child)


class CommonParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return True  # Default parser

    @classmethod
    def extract_urls(cls, source_url: str, document) -> Iterable[str]:
        if document is None:
            return []

        document = build_document(document, clean=True)

        document.strip_tags(TAGS_WITHOUT_CONTENT)
        document.strip_tags(SERVICE_TAGS)
        for link in document.css("a"):
            recursive_delete(link)
            link_text = link.text()

            if not link_text or link_text is None:
                continue

            if not is_valid_link_text(link_text):
                continue
            href = link.attrs["href"] if "href" in link.attrs else None
            url = get_absolute_url(source_url, href)
            if not is_correct_article_link(url):
                continue
            if is_path_ignored(url):
                continue
            if is_rss_link(url):
                continue
            yield url
