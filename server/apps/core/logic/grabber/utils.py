# Some functions that used across different modules
import dateparser
from datetime import datetime

def convert_date_format(date_string: str) -> str:
    '''
    Parse data string and return in format %Y-%m-%d
    '''
    current_date = datetime.now().strftime('%Y-%m-%d')

    if not date_string:
        return current_date

    date_obj = dateparser.parse(date_string, languages=['en', 'ru'])
    if date_obj:
        utc_date = date_obj.strftime('%Y-%m-%d')
        return utc_date
    else:
        print("Invalid date format: ", date_string)
        return current_date
