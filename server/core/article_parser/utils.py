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
