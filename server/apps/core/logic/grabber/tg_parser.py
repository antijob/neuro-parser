from selectolax.parser import HTMLParser
import requests
import re
from collections import namedtuple
from datetime import datetime
from icecream import ic


ArticleData = namedtuple('ArticleData', 'title text date final_url')


def add_s_to_url(url: str):
    if url.startswith('https://t.me/'):
        new_url = url.replace('https://t.me/', 'https://t.me/s/')
        return new_url
    else:
        raise ValueError("Wrong url format, it should start with https://t.me")


def get_first_sentence(text):
    # Regular expression pattern to match the first sentence
    pattern = r'^(.*?[.!?])\s'

    # Use re.search to find the first occurrence of the pattern
    match = re.search(pattern, text)

    if match:
        first_sentence = match.group(1)
        return first_sentence.strip()
    else:
        # If no match is found, return the entire text as the first sentence
        return text.strip()

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
    Then parse data on [url]?embed=1
    Returns data from this page - text, title, date, url
    '''
    # ic(url)
    params = {'embed': '1'}
    page = requests.get(url, params)
    tree = HTMLParser(page.text)
    # text = tree.css_first('div.tgme_widget_message_text').text()
    text_tag = tree.css_first('div.tgme_widget_message_text')
    if text_tag is not None:
        text = text_tag.text()
        title = text.split(sep='\n')[0]
        if len(title) > 100:
            title = get_first_sentence(text)
    else:
        text = ''
        title = ''

    # if text:
    #     title = text.split(sep='\n')[0]
    #     if len(title) > 100:
    #         title = get_first_sentence(text)
    # else:
    #     title = ''
    time_tag = tree.css_first('time.datetime')
    date_time = time_tag.attributes['datetime']
    original_datetime = datetime.fromisoformat(date_time)
    date = original_datetime.strftime("%Y-%m-%d")
    return ArticleData(title, text, date, url)


