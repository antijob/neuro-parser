import re
from urllib.parse import urlparse, urljoin, unquote

from django.conf import settings
from lxml import cssselect, etree

import feedparser
from icecream import ic

from .article_parser import (
    count_links,
    get_document,
    MIN_WORDS_IN_SENTENCE,
    SERVICE_TAGS,
    text_content)
from .tg_parser import extract_tg_urls
from .vk_parser import extract_vk_urls
from .ok_parser import extract_ok_urls

# ToDo: move this part to proper place
ic.configureOutput(prefix='')


IGNORED_PATHS = [
    'about', 'stat', 'statistics', 'statistika', 'statisticheskie-dannyie',
    'contacts', 'kontakty', 'search', 'feedback',
    'internet-priemnaya', 'priemnaya', 'reception', 'icenter', 'for-people',
    'housing', 'internet-and-reception',
    'structure', 'struktura', 'staff', 'kadry', 'kadrovoe-obespechenie',
    'management', 'guide',
    'job', 'vacancy', 'recruit', 'priem-na-sluzhbu', 'vacancies',
    'sitemap', 'map_site', 'help', 'faq', 'links', 'karta-sajta', 'pda',
    'documents', 'docs', 'dokumenty', 'mailing', 'for-mass-media',
    'video', 'video_soc', 'audio', 'photo', 'media', 'gallery', 'photogallery',
    'fotogalereya',
    'goods', 'zakupki', 'goszakupki', 'zakaz', 'gosudarstvennye-zakupki',
    'purchases', 'contests',
    'citizens', 'priem-grazhdan', 'peopleware', 'predprinimatelyam',
    'poryadok-obrashheniya-grazhdan',
    'uvedomlenie-ob-ekstremizme', 'uvedomleniya-ob-ekstremizme',
    'borba-s-ekstremizmom', 'extremism', 'antiterror',
    'prokuratura-razyasnyaet', 'explain', 'pravovoe-prosveshhenie',
    'zapros-ot-smi', 'rules', 'plan', 'k-svedeniyu-smi',
    'press-sluzhba', 'k-svedeniyu', 'vzaimodeystvie-so-smi',
    'mass-communications',
    'nurnberg', 'nyurnbergskiy-process', 'history', 'istoriya',
    'veteran', 'sovet-veteranov', 'veterans',
    'against', 'verify', 'colleg', 'control', 'projects',
    'attention', 'service', 'references', 'folder', 'law_info',
    'anti_corruption', 'corruption', 'anticor', 'borba-s-korrupcziej',
    'protivodejstvie-korruptsii', 'anticorruption', 'finance',
    'anti-corruption', 'antinar', 'antinark', 'tender',
    'regions', 'prosecutors-offices-of-region', 'acts', 'anounce', 'anounces',
    'programma-territoriya-zakona', 'usloviya-ispolzovaniya-sayta', 'sluzhba',
    'oficialnyy-banner', 'requirements', 'education', 'coordination',
    'o-razrabotke-sayta', 'usloviya-ispolzovaniya-sayta', 'audit',
    'government-service', 'chamber-of-commerce'
]
ACCEPTABLE_EXTENSIONS = ['htm', 'html', 'shtml', 'php', 'asp', 'jsp']

NEXT_PAGE_LINK_TEXTS = ['следующая', '>', '»', '›', '>>',
                        'предыдущие записи', 'вперед']


def is_valid_link_text(link_text):
    too_short = len(link_text.split()) < MIN_WORDS_IN_SENTENCE
    if not too_short:
        return True
    if ('подробнее' in link_text.lower()
            or 'читать полностью' in link_text.lower()
            or 'читать далее' in link_text.lower()):
        return True
    return False


def is_inside_service_tag(node):
    while True:
        parent = node.getparent()
        if parent is None:
            return False
        if parent.tag in SERVICE_TAGS:
            return True
        node = parent


def extract_html_urls(source_url, document):
    """Returns article urls found on the news list page."""

    if document is None:
        return []
    links = cssselect.CSSSelector('a')(document)

    for link in links:
        if is_inside_service_tag(link):
            continue
        link_text = text_content(link, long_text_only=False, include_links=True).strip()
        if not is_valid_link_text(link_text):
            continue
        url = get_absolute_url(source_url, link.get('href'))
        if not is_correct_article_link(url):
            continue
        if is_path_ignored(url):
            continue
        if not is_rss_link(url):
            # print(url)
            yield url


def has_acceptable_extension(path):
    splitted = path.split('.')
    if len(splitted) < 2:
        return True
    return splitted[-1] in ACCEPTABLE_EXTENSIONS


def remove_extension(path):
    splitted = path.split('.')
    if len(splitted) < 2:
        return path
    if splitted[-1] in ACCEPTABLE_EXTENSIONS:
        return path[:-(1 + len(splitted[-1]))]


def is_path_ignored(url):
    path = str(urlparse(url).path)
    if not has_acceptable_extension(path):
        return True
    splitted_path = remove_extension(path).split('/')
    if 'news' in splitted_path:
        return False
    for ignored in IGNORED_PATHS:
        if ignored in splitted_path:
            return True


def get_absolute_url(source_url, url):
    source_domain = urlparse(source_url).netloc
    link_domain = urlparse(url).netloc
    if not link_domain:
        link_domain = source_domain
        url = urljoin(source_url, url)
    if source_domain == link_domain:
        return url
    return None


def is_correct_article_link(url):
    if not url:
        return False
    if not url.startswith('http'):
        return False
    link_query = urlparse(url).query
    link_path = urlparse(url).path.strip('/')
    return link_path or link_query


def find_rss_urls(source_url, document):
    """Finds URLs to rss-files on page."""
    ic('find_rss_urls')
    # ic(source_url, document)
    ic(source_url)
    if document is None:
        ic('return empty')
        return []
    links = cssselect.CSSSelector('a')(document)
    links += cssselect.CSSSelector('link')(document)
    # ic(links)
    for link in links:
        url = link.get('href')
        absolute_url = get_absolute_url(source_url, url)
        if is_rss_link(absolute_url):
            ic(absolute_url)
            yield absolute_url


def is_rss_link(url):
    # ic("is_rss_link")
    path = str(urlparse(url).path)
    return 'rss' in path or path.endswith('.xml') or 'feed' in path


def find_articles_urls_in_rss(document):
    """Finds article urls in rss-document."""

    if document is None:
        return []
    if not document[0] or not document[0][0].tag == 'rss':
        return
    links = cssselect.CSSSelector('link')(document)
    for link in links:
        text = link.text or ''
        tail = link.tail or ''
        url = (text + tail).strip()
        if url:
            yield url


def extract_rss_urls(source_url, document):
    """Extracts article urls using RSS"""
    ic('extract_rss_urls')
    if document is None:
        return []
    rss_urls = find_rss_urls(source_url, document)
    for rss_url in rss_urls:
        # parse each rss_url for article links
        # ic(rss_url)
        data_parsed = feedparser.parse(rss_url)
        article_urls = [art.link for art in data_parsed.entries]
        # ic(article_urls)
        absolute_urls = (get_absolute_url(source_url, url)
                         for url in article_urls)
        for article_url in absolute_urls:
            if is_correct_article_link(article_url):
                # ic(article_url)
                yield article_url


def unquote_urls(urls):
    return (unquote(url) for url in urls if url)


def extract_all_news_urls(url: str):
    # ic('extract_all_news_urls')

    tg_urls = None
    if url.startswith('https://t.me/'):
        tg_urls = set(unquote_urls(extract_tg_urls(url)))
    if tg_urls:
        return tg_urls

    vk_urls = None
    if url.startswith('https://vk.com/'):
        vk_urls = set(unquote_urls(extract_vk_urls(url)))
    if vk_urls:
        return vk_urls

    ok_urls = None
    if url.startswith('https://ok.ru/'):
        ok_urls = set(unquote_urls(extract_ok_urls(url)))
    if ok_urls:
        return ok_urls

    document = get_document(url)
    if document is None:
        return

    rss_urls = set(unquote_urls(extract_rss_urls(url, document)))
    if rss_urls:
        return rss_urls

    html_urls = set(unquote_urls(extract_html_urls(url, document)))
    return html_urls


def is_pagination_block(node):
    if node is None:
        return False
    text = text_content(node, long_text_only=False, include_links=True)
    word_count = len([word for word in text.split() if len(word) > 1])
    if not word_count:
        return False

    # Pagination block contains many links and few words
    if count_links(node) / word_count < 0.5:
        return False

    # Pagination block should contain page numbers
    if re.search(r'\d+[\s\|]+\d+[\s\|]+', text):
        return True


def find_pagination_block(node):
    """Returns block with page links"""

    if node is None:
        return
    if isinstance(node, etree._Comment):
        return

    pagination_classes = ['pages', 'pagination']
    for klass in pagination_classes:
        pages = cssselect.CSSSelector('.{}'.format(klass))(node)
        if pages:
            return pages[0]

    if is_pagination_block(node):
        return node
    for subnode in node:
        pagination_block = find_pagination_block(subnode)
        if pagination_block is not None:
            return pagination_block


def find_next_page_url(page_block, next_page):
    links = cssselect.CSSSelector('a')(page_block)
    for link in links:
        text = text_content(link, long_text_only=False, include_links=True)
        if text.lower().strip() == str(next_page):
            return link.get('href')
        if text.lower().strip() in NEXT_PAGE_LINK_TEXTS:
            return link.get('href')


def download_articles_since_date(articles, start_date):
    for a in articles:
        a.download()

    publication_dates = [(article.publication_date, article.url)
                         for article in articles
                         if article.publication_date]

    # Stop parsing if articles have no publication_date
    if not publication_dates:
        for article in articles:
            article.delete()
        return False

    publication_dates = sorted(publication_dates, key=lambda x: x[0])
    min_publication_date = publication_dates[len(publication_dates) // 2]
    return min_publication_date[0] > start_date


def grab_archive(source, first_page_url=None, first_page=1, start_date=None):
    page = first_page
    page_url = first_page_url or source.url
    parsing = True
    while parsing:
        news_list = get_document(page_url)

        # Get next page link
        page_block = find_pagination_block(news_list)
        if page_block is None:
            return

        # Grab article links
        article_urls = set(unquote_urls(extract_html_urls(page_url, news_list)))
        if not article_urls:
            return
        articles = source.add_articles(article_urls)

        # Grab article data
        if articles:
            parsing = download_articles_since_date(articles, start_date)

        # Get url for next page
        page += 1
        relative_url = find_next_page_url(page_block, page)
        if relative_url:
            page_url = get_absolute_url(page_url, relative_url)
        else:
            parsing = False

        if page > 500:
            parsing = False

    return True
