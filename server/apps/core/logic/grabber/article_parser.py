import datetime
import re
from collections import namedtuple
import dateparser
import requests
from lxml import cssselect, etree
from lxml.html.clean import Cleaner
from goose3 import Goose
from goose3.configuration import Configuration
from icecream import ic
from .user_agent import random_headers
from .utils import convert_date_format
from .tg_parser import get_tg_page_data, parse_tg_raw_data
from .vk_parser import get_vk_page_data, parse_vk_raw_data
from .ok_parser import get_ok_page_data, parse_ok_raw_data


MIN_WORDS_IN_SENTENCE = 5
MIN_WORDS_IN_ARTICLE = 50
SERVICE_TAGS = ['script', 'style', 'head', 'aside']
TAGS_WITHOUT_CONTENT = ['form', 'select', 'input', 'textarea', 'button']
BLOCK_TAGS = [
    "address", "article", "aside", "blockquote", "canvas", "dd", "div", "dl",
    "dt", "fieldset", "figcaption", "figure", "footer", "form", "h1", "h2",
    "h3", "h4", "h5", "h6", "header", "li", "main", "nav", "ol", "p", "pre",
    "section", "table", "tfoot", "ul"]
HEADINGS = ('h1', 'h2', 'h3', 'h4', 'h5', 'h6')
IGNORED_IDS = ['comments_block', 'seo']
IGNORED_CLASSES = [
    'print-data', 'alert-warning', 'breadcrumb-list', 'feeds-page__header',
    'feeds-page__navigation', 'feeds-page__title', 'button', 'btn',
    'subscribe__popover_field', 'news_image', 'donate_text', 'img',
    'social-block', 'news_date', 'crumb', 'svg', 'twitter-share-button',
    'rpbt_shortcode', 'tags', 'overtitle', 'date-and-region', 'main-thematic',
    'related-gallery', 'mz-publish__sidebar', 'mz-layout-content__col-main']
KNOWN_ARTICLE_CLASSES = [
    'news_content', 'feeds-page__article_text', 'article-boxes-list',
    'mz-publish__text', 'GeneralMaterial-article', 'news-detail__text',
    'text-block']

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
    kill_tags=['img', 'noscript', 'button'],
    remove_unknown_tags=True,
    safe_attrs_only=False,
)

ArticleData = namedtuple('ArticleData', 'title text date final_url')


def get_document(url, clean=False):
    """ Get document by given url,
        cleans it if clean = True and return etree document
    """
    headers = random_headers()
    try:
        if url.startswith('https://t.co/'):
            response = requests.get(url)
        else:
            response = requests.get(url, headers=headers, timeout=8)
    except requests.exceptions.RequestException:
        return
    if not response.status_code == 200:
        return
    html = decoded(response)
    html = html.replace("\xa0", " ")
    if html and clean:
        html = CLEANER.clean_html(html)
    try:
        document = etree.HTML(html)
    except ValueError:
        document = etree.HTML(response.content)
    document.set("url", response.url)
    return document


def decoded(response):
    encodings = ('utf-8', 'cp1251', 'cp866', 'koi8-r')
    for encoding in encodings:
        try:
            return response.content.decode(encoding)
        except UnicodeDecodeError:
            pass


def remove_double_spaces(text):
    text = text.lstrip()
    while '  ' in text:
        text = text.replace('  ', ' ')
    while ' \n' in text:
        text = text.replace(' \n', '\n')
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')
    return text


def text_content(node, long_text_only=False, include_links=True):
    """Returns text content of node and its children.
    Ignores headings and service tags."""
    if node is None:
        return ''
    if node.tag in SERVICE_TAGS:
        return ''
    if node.tag in TAGS_WITHOUT_CONTENT:
        return ''
    if node.tag is etree.Comment:
        return ''

    node_id = node.get('id')
    if node_id:
        for id_ in IGNORED_IDS:
            if id_ in node_id:
                return ''
    node_classes = node.get('class', '').split()
    if node_classes:
        for class_ in IGNORED_CLASSES:
            if class_ in node_classes:
                return ''

    if not include_links:
        dot_count = ((node.text or '') + (node.tail or '')).count(".")
        link_count = count_links(node)
        if link_count >= max(dot_count, 3):
            return ''

    # Concat node text and its children texts
    children_text = children_text_content(node, long_text_only, include_links)
    text = (node.text or '') + children_text + (node.tail or '')
    if long_text_only and len(text.split()) < MIN_WORDS_IN_SENTENCE:
        return ''
    if node.tag in BLOCK_TAGS:
        text += "\n\n"
    else:
        text += " "
    return remove_double_spaces(text)


def children_text_content(node, long_text_only, include_links):
    if node is None:
        return ''

    klass = node.get('class', '')
    if 'menu' in klass or 'footer' in klass:
        return ''

    texts = []
    for child in node:
        if child.tag != 'h1':
            content = text_content(child, long_text_only, include_links)
            if content:
                texts += [content]
            else:
                child.getparent().remove(child)
    return ''.join(texts)


def count_links(node):
    count = 0
    for subnode in node:
        if subnode.tag == 'a':
            count += 1
        else:
            count += count_links(subnode)
    return count


def is_article(node):
    if node.tag in SERVICE_TAGS or node.tag is etree.Comment:
        return False
    if 'article' in node.get('class', '').split():
        return True
    if 'article' in node.get('id', '').split():
        return True
    text = text_content(node, long_text_only=False, include_links=True)

    # Article should contain a lot of words
    word_count = len(text.split())
    if word_count < MIN_WORDS_IN_ARTICLE:
        return False

    # Article should not contain a lot of links
    link_count = count_links(node)
    if link_count > (text.count('.') + text.count(',')):
        return False
    if link_count > len(text.split()) / MIN_WORDS_IN_SENTENCE:
        return False

    # Article contains punctuation marks
    punctuation_count = text.count('.') + text.count(',')
    if punctuation_count < (word_count / MIN_WORDS_IN_SENTENCE / 3):
        return False

    # Article's parent tag contains almost the same text as article
    parent = node.getparent()
    parent_text = (parent.text or '') + (parent.tail or '')
    parent_word_count = len(parent_text.split())
    return (parent_word_count / word_count) < MIN_WORDS_IN_SENTENCE


def extract_heading(node, heading=None):
    """Returns most important heading tag subnode"""

    genproc_title = node.xpath("//div[@id = 'text_printprw']")
    if genproc_title:
        return text_content(genproc_title[0]).strip()

    h1 = node.xpath("//h1")
    if h1:
        return text_content(h1[0], include_links=True, long_text_only=False).strip()

    for subnode in node:
        if subnode.tag not in HEADINGS:
            continue
        if heading is None or subnode.tag < heading.tag:
            heading = subnode
    if heading is None:
        return ''
    return text_content(heading, include_links=True, long_text_only=False).strip()


def find_text_chunks(node):
    """Returns list on nodes with significant text chunks"""

    if node is None:
        return []
    texts = set()
    for subnode in node:
        if is_article(subnode):
            texts.add(subnode)
        texts.update(find_text_chunks(subnode))
    return texts


def find_node_with_article(tree):
    text_nodes = find_text_chunks(tree)
    if len(text_nodes) == 0:
        return
    elif len(text_nodes) == 1:
        return text_nodes.pop()
    else:
        longest = max(text_nodes,
                      key=lambda x: len(text_content(x,
                                                     include_links=True,
                                                     long_text_only=False)))
        return longest

def get_article(url) -> ArticleData:
    """ Get url of article
        Grab data from posts on tg, vk, ok, websites
        Returns title, text, date, url as a namedtuple
    """
    if url.startswith('https://t.me/'):
        return get_tg_page_data(url)

    if url.startswith('https://vk.com/'):
        return get_vk_page_data(url)

    if url.startswith('https://ok.ru/'):
        return get_ok_page_data(url)


    config = Configuration()
    config.strict = False  # turn of strict exception handling
    # config.browser_user_agent = random_headers() # set the browser agent string
    config.http_timeout = 8  # set http timeout in seconds

    with Goose(config) as g:
        article = g.extract(url=url)
        title = article.title
        text = article.cleaned_text
        final_url = article.final_url
        date = convert_date_format(article.publish_date)

    # date = extract_date(article.doc, article.top_node, final_url)

    return ArticleData(title, text, date, final_url)


def parse_article_raw_data(url, data) -> ArticleData:

    if url.startswith('https://t.me/'):
        return parse_tg_raw_data(url)

    if url.startswith('https://vk.com/'):
        return parse_vk_raw_data(url)

    if url.startswith('https://ok.ru/'):
        return parse_ok_raw_data(url)


    config = Configuration()
    config.strict = False

    with Goose(config) as g:
        article = g.extract(raw_html=data)
        title = article.title
        text = article.cleaned_text
        final_url = article.final_url
        date = convert_date_format(article.publish_date)

    return ArticleData(title, text, date, final_url)

