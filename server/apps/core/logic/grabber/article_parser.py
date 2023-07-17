import datetime
import re
from collections import namedtuple
from random import choice
import dateparser
import requests
from lxml import cssselect, etree
from lxml.html.clean import Cleaner
from goose3 import Goose
from goose3.configuration import Configuration
from icecream import ic


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
USER_AGENTS = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
               'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
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


def random_headers():
    ic('random_headers')
    ua = choice(USER_AGENTS)
    # print(type(ua))
    head = {'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    # print(head, type(head), sep='\n\n')
    # return {'User-Agent': choice(USER_AGENTS),
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'}
    return head


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


# def get_article_old(url):
    # """Returns title and text of article."""

    # tree = get_document(url, clean=True)
    # if tree is None:
    #     return

    # final_url = tree.get("url")
    # title = extract_heading(tree)
    # if not title:
    #     title_tag = tree.find(".//title")
    #     title = title_tag.text if title_tag is not None else ''

    # # looking by article tag, then by lins of known classes,
    # # then by article class and then by longest text of node
    # article = find_article_tag(tree)
    # if article is None:
    #     article = find_by_known_class(tree)
    # if article is None:
    #     article = find_article_class(tree)
    # if article is None:
    #     article = find_node_with_article(tree)
    # if article is None:
    #     return

    # text = text_content(article,
    #                     include_links=True,
    #                     long_text_only=False).strip()
    # date = extract_date(tree, article, final_url)
    # return ArticleData(title, text, date, final_url)

def get_article(url) -> ArticleData:
    """Get url of article
        Returns title, text, date, url as a namedtuple
    """
    config = Configuration()
    config.strict = False  # turn of strict exception handling
    # config.browser_user_agent = random_headers() # set the browser agent string
    config.http_timeout = 8  # set http timeout in seconds

    with Goose(config) as g:
        article = g.extract(url=url)
        title = article.title
        text = article.cleaned_text
        final_url = article.final_url

    date = extract_date(article.doc, article.top_node, final_url)

    return ArticleData(title, text, date, final_url)

def find_article_tag(node):
    if node is None:
        return
    articles = cssselect.CSSSelector('article')(node)
    if len(articles) == 1:
        return articles[0]


def find_article_class(node):
    if node is None:
        return
    for subnode in node:
        if subnode.tag in SERVICE_TAGS or subnode.tag is etree.Comment:
            continue
        class_ = subnode.get('class', '').split()
        if 'article' in class_:
            return subnode
    for subnode in node:
        article = find_article_class(subnode)
        if article is not None:
            return article


def find_by_known_class(node):
    for klass in KNOWN_ARTICLE_CLASSES:
        article = cssselect.CSSSelector('.{}'.format(klass))(node)
        if article:
            return article[0]


def is_date(node):
    text = (node.text or '') + (node.tail or '')
    descriptions = [
        'Опубликовано:', 'Создано:', 'Дата публикации:', 'Время публикации:', 'года']
    for description in descriptions:
        text = (text.replace(description, ''))
    try:
        parsed_date = dateparser.parse(text, languages=['ru'])
    except RecursionError:
        # TODO: Refactoring
        return False
    if parsed_date:
        return parsed_date.date()


def extract_date(tree, article_node, url):
    date = find_date_in_url(url)
    if date:
        return date
    date = find_date_by_class(tree)
    if date:
        return date
    date = find_date_in_siblings(article_node)
    if date:
        return date
    date = find_date_in_subnodes(article_node)
    if date and date <= datetime.date.today():
        return date


def find_date_in_url(url):
    match = re.search(r'\/(\d{4}([\/\-])\d{2}\2\d{2})(\/.*)?$', url)
    if match:
        return dateparser.parse(match.groups()[0])


def find_date_by_class(tree):
    classes = ["feeds-page__info_item"]
    for klass in classes:
        elements = cssselect.CSSSelector(".%s" % klass)(tree)
        if elements:
            return find_date_in_subnodes(elements[0])


def find_date_in_subnodes(node):
    if node is None:
        return
    date = is_date(node)
    if date:
        return date

    for subnode in node:
        date = find_date_in_subnodes(subnode)
        if date:
            return date


def find_date_in_siblings(node):
    if node is None:
        return

    previous = node.getprevious()
    while True:
        if previous is None:
            break
        date = find_date_in_subnodes(previous)
        if date:
            return date
        previous = previous.getprevious()

    next_ = node.getnext()
    while True:
        if next_ is None:
            break
        date = find_date_in_subnodes(next_)
        if date:
            return date
        next_ = next_.getnext()
