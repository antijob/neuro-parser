# -*- coding: utf-8 -*-

import datetime
import re


def day_in_words(day):
    numeral_days = (
        'первого', 'второго', 'третьего', 'четвёртого', 'пятого',
        'шестого', 'седьмого', 'восьмого', 'девятого', 'десятого',
        'одиннадцатого', 'двенадцатого', 'тринадцатого', 'четырнадцатого',
        'пятнадцатого', 'шестнадцатого', 'семнадцатого', 'восемнадцатого',
        'девятнадцатого', 'двадцатого')
    if day <= 20:
        return numeral_days[day - 1]
    elif day == 30:
        return 'тридцатого'
    elif day == 31:
        return 'тридцать первого'
    else:
        day = day - 21
        return "двадцать " + numeral_days[day]


def month_in_words(m):
    numeral_months = ("января", "февраля", "марта", "апреля", "мая", "июня",
                      "июля", "августа", "сентября", "октября", "ноября",
                      "декабря")
    return numeral_months[m - 1]


def year_in_words(year):
    two_thousand = "две тысячи "
    n = year % 100
    ONES = ["первого", "второго", "третьего", "четвертого", "пятого",
            "шестого", "седьмого", "восьмого", "девятого", "десятого",
            "одиннадцатого", "двенадцатого", "тринадцатого", "четырнадцатого",
            "пятнадцатого", "шестнадцатого", "семнадцатого", "восемнадцатого",
            "девятнадцатого"]
    TENS = {20: "двадцать", 30: "тридцать", 40: "сорок", 50: "пятьдесят",
            60: "шестьдесят", 70: "семьдесят", 80: "восемьдесят",
            90: "девяносто"}
    ROUND_TENS = {10: "десятого", 20: "двадцатого", 30: "тридцатого",
                  40: "сорокового", 50: "пятидесятого", 60: "шестидесятого",
                  70: "семидесятого", 80: "восьмидесятого", 90: "девяностого"}
    if n < 20:
        return two_thousand + ONES[n - 1] + " года"
    elif n % 10 == 0:
        return two_thousand + ROUND_TENS[n] + " года"
    else:
        ones = n % 10
        tens = n - ones
        return two_thousand + "{} {} года".format(TENS[tens], ONES[ones])


def date_in_words(date):
    y, m, d = date.timetuple()[:3]
    day = day_in_words(d)
    month = month_in_words(m)
    year = year_in_words(y)
    return "{} {} {}".format(day, month, year)


def format_dd_month_yyyy(date):
    year, m, d = date.timetuple()[:3]
    day = "«%02d»" % d
    month = month_in_words(m)
    return "{} {} {}".format(day, month, year)


def format_if_date(string):
    m = re.match(r"^\d{4}-\d{2}-\d{2}$", string)
    if not m:
        return string
    y, m, d = map(int, string.split("-"))
    try:
        date = datetime.date(y, m, d)
    except ValueError:
        return string
    return format_dd_month_yyyy(date)
