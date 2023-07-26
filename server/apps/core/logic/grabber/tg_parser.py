from selectolax.parser import HTMLParser
import requests
from collections import namedtuple
from datetime import datetime


ArticleData = namedtuple('ArticleData', 'title text date final_url')


def add_s_to_url(url: str):
    if url.startswith('https://t.me/'):
        new_url = url.replace('https://t.me/', 'https://t.me/s/')
        return new_url
    else:
        raise ValueError("Wrong url format, it should start with https://t.me")


def extract_tg_urls(url: str):
    '''
    yields all links to pages with news
    '''
    if '/s/' not in url:
        url = add_s_to_url(url)
    page = requests.get(url)
    tree = HTMLParser(page.text)

    for node in tree.css('a.tgme_widget_message_date'):
        yield node.attributes['href']


def get_tg_page_data(url):
    '''
    Gets url of post on t.me site
    Returns data from this page - text, title, date, url
    '''

    page = requests.get(url)
    tree = HTMLParser(page.text)

    meta_tag = tree.css_first('meta[property="og:description"]')
    if meta_tag:
        text = meta_tag.attributes.get('content')
        title = text.split(sep='\n')[0]

    params = {'embed': '1'}
    page_time = requests.get(url, params)
    tree_time = HTMLParser(page_time.text)
    time_tag = tree_time.css_first('time.datetime')
    date_time = time_tag.attributes['datetime']
    original_datetime = datetime.fromisoformat(date_time)
    date = original_datetime.strftime("%Y-%m-%d")

    return ArticleData(title, text, date, url)


