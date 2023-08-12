# Some functions that used across different modules
import dateparser

def convert_date_format(date_string: str) -> str:
    '''
    Parse data string and return in format %Y-%m-%d
    '''
    # date_obj = dateparser.parse(date_string, languages=['en', 'ru'], settings={'TO_TIMEZONE': 'UTC'})
    date_obj = dateparser.parse(date_string, languages=['en', 'ru'])
    if date_obj:
        utc_date = date_obj.strftime('%Y-%m-%d')
        return utc_date
    else:
        return "Invalid date format!"
