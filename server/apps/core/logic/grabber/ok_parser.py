import requests
from selectolax.parser import HTMLParser
from random import choice
import dateparser
import re
from .user_agent import random_headers
from collections import namedtuple

ArticleData = namedtuple('ArticleData', 'title text date final_url')

def extract_ok_urls(url: str):
    '''
    Generates links to pages with news from given public url
    '''
    page = requests.get(url, headers=random_headers())
    tree = HTMLParser(page.text)

    for node in tree.css('a.media-text_a'):
        news_page_link = 'https://ok.ru' + node.attributes['href']
        # print("Link: ", news_page_link)
        yield news_page_link

def convert_to_utc(date_string: str) -> str:
    '''
    Parse data string and returns it in UTC format
    '''
    # print(f'date_string: {date_string}')
    date_obj = dateparser.parse(date_string, languages=['en', 'ru'])
    if date_obj:
        # Convert the datetime object to UTC timezone
        utc_date = date_obj.strftime('%Y-%m-%d')
        return utc_date
    else:
        return "Invalid date format!"

def get_first_sentence(text: str) -> str:
    '''
    Extracts the first sentence from given text
    '''
    pattern = r'^[^.!?]+[.!?]'
    match = re.search(pattern, text)

    return match.group(0) if match else ''

def get_ok_page_data(url: str):
    '''
    Gets url of post page on ok.ru
    Returns data from this page - text, title, date, url
    '''

    page = requests.get(url, headers=random_headers())
    tree = HTMLParser(page.text)
    text = tree.css_first('div.media-text_cnt_tx').text()
    if text:
        title = text.split(sep='\n')[0]
        if len(title) > 100:
            title = get_first_sentence(text)
    else:
        title = ''
    date = convert_to_utc(tree.css_first('div.ucard_add-info_i').text())

    # print(text, end='\n\n')
    # print(title, end='\n\n')
    # print(date, end='\n\n')

    return ArticleData(title, text, date, url)

