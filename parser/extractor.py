from readability import Document
import html2text
import re
from ner import datefinder, eventfinder
import datetime
from calendar import monthrange
from utils.str import remove_tuples


def normalize_newlines(text):
    text = re.sub("\n+", "\n", text)
    return text


def parse_html(html_text):
    doc = Document(html_text)
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_tables = True
    h.emphasis_mark = ''
    h.strong_mark = ''
    h.ignore_images = True
    h.unicode_snob = True
    h.body_width = 0
    h.wrap_links = False
    try:
        return normalize_newlines(doc.title() + '\n' + h.handle(doc.summary()))
    except:
        return ""


def extract_events(doc):
    lines = doc.split('\n')
    res = list()
    for i, line in enumerate(lines):
        dates = datefinder.find_dates(line)
        filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), dates))
        if len(filtered_dates) != 0:
            eventtext = eventfinder.find_event(lines, i)
            if eventtext != "":
                y = find_year(filtered_dates)
                filtered_dates.sort(key=lambda d: (d.fact.year if d.fact.year is not None
                                                   else y,
                                                   d.fact.month, d.fact.day), reverse=True)

                year = filtered_dates[0].fact.year if filtered_dates[0].fact.year is not None else y
                month = filtered_dates[0].fact.month
                day = filtered_dates[0].fact.day
                try:
                    date = datetime.date(year, month, day)
                except ValueError:
                    if month > 12:
                        month = 12
                    _, day = monthrange(year, month)
                    date = datetime.date(year, month, day)
                res.append((eventtext, date))
    remove_tuples(res)
    return res


def find_year(dates):
    year = 0
    for d in dates:
        if d.fact.year is not None:
            if d.fact.year > year:
                year = d.fact.year
    if year == 0:
        year = datetime.datetime.now().year
    return year
