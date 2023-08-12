import requests
from selectolax.parser import HTMLParser
from random import choice
from collections import namedtuple
import re
from .user_agent import random_headers
from .utils import convert_date_format

ArticleData = namedtuple('ArticleData', 'title text date final_url')

def extract_vk_urls(url: str):
    '''
    Generates links to pages with news from given public url
    '''
    page = requests.get(url, headers=random_headers())
    tree = HTMLParser(page.text)

    for node in tree.css('a.PostHeaderSubtitle__link'):
        news_page_link = 'https://vk.com' + node.attributes['href']
        # print("Link: ", news_page_link)
        yield news_page_link

def get_first_sentence(text: str) -> str:
    '''
    Extracts the first sentence from given text
    '''
    pattern = r'^[^.!?]+[.!?]'
    match = re.search(pattern, text)

    return match.group(0) if match else ''

def get_vk_page_data(url: str):
    '''
    Gets url of post page on vk.com
    Returns data from this page - text, title, date, url
    '''

    page = requests.get(url, headers=random_headers())
    tree = HTMLParser(page.text)
    text = tree.css_first('div.wall_post_text').text()
    if text:
        title = text.split(sep='\n')[0]
        if len(title) > 100:
            title = get_first_sentence(text)
    else:
        title = ''
    date = convert_date_format(tree.css_first('time.PostHeaderSubtitle__item').text())

    # print(text, end='\n\n')
    # print(title, end='\n\n')
    # print(date, end='\n\n')

    return ArticleData(title, text, date, url)
