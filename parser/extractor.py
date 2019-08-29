from readability import Document
import html2text
import re
from ner import datefinder, eventfinder
import datetime
from datetime import datetime as dt
from calendar import monthrange
from utils.str import remove_tuples
from urllib.parse import urlsplit


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


# def extract_events(doc):
#     lines = doc.split('\n')
#     res = list()
#     for i, line in enumerate(lines):
#         dates = datefinder.find_dates(line)
#         filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), dates))
#         if len(filtered_dates) != 0:
#             eventtext = eventfinder.find_event(lines, i)
#             if eventtext != "":
#                 y = find_year(filtered_dates)
#                 filtered_dates.sort(key=lambda d: (d.fact.year if d.fact.year is not None
#                                                    else y,
#                                                    d.fact.month, d.fact.day), reverse=True)
#
#                 year = filtered_dates[0].fact.year if filtered_dates[0].fact.year is not None else y
#                 month = filtered_dates[0].fact.month
#                 day = filtered_dates[0].fact.day
#                 try:
#                     date = datetime.date(year, month, day)
#                 except ValueError:
#                     if month > 12:
#                         month = 12
#                     _, day = monthrange(year, month)
#                     date = datetime.date(year, month, day)
#                 res.append((eventtext, date))
#     remove_tuples(res)
#     return res


# TODO: think of a better approach
def year_from_url(url):
    pattern = re.compile("20[1-2][0-9]")
    res = urlsplit(url).path
    match = re.search(pattern, res)
    if match is not None:
        return int(match.group(0))
    return None


def extract_events_better(doc, url):
    # all_dates = datefinder.find_dates(doc)
    lines = doc.split('\n')
    year_in_case = year_from_url(url)
    res = list()
    for i, line in enumerate(lines):
        dates = datefinder.find_dates(line)
        dates_for_year = datefinder.find_dates('\n'.join(lines[i-5:i+6]))
        default_year = find_year(dates_for_year, year_in_case)
        filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), dates))
        if len(filtered_dates) != 0:
            eventtext = eventfinder.find_event(lines, i)
            if eventtext != "":
                y = find_year(dates, default_year)
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


def extract_events_better_newspaper(doc, url):
    all_dates = datefinder.find_dates(doc)
    filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), all_dates))
    if len(filtered_dates) > 5:
        return []
    lines = doc.split('\n')
    year_in_case = year_from_url(url)
    # if not year_in_case:
    #     year_in_case = find_year(datefinder.find_dates(html), None)
    res = list()
    for i, line in enumerate(lines):
        dates = datefinder.find_dates(line)
        dates_for_year = datefinder.find_dates('\n'.join(lines[i - 5:i + 6]))
        default_year = find_year(dates_for_year, year_in_case)
        filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), dates))
        if 0 < len(filtered_dates):
            eventtext = eventfinder.find_event(lines, i)
            if eventtext != "":
                y = find_year(dates, default_year)
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


def find_year(dates, default_year):
    year = 0
    for d in dates:
        if d.fact.year is not None:
            if d.fact.year > year:
                year = d.fact.year
    if year == 0:
        if default_year is not None:
            year = default_year
        else:
            year = datetime.datetime.now().year
    return year


def extract_events_from_vk(post):
    res = list()
    dates = datefinder.find_dates(post['text'])
    default_year = dt.utcfromtimestamp(post['date']).year
    filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), dates))
    if len(filtered_dates) != 0:
        eventtext = eventfinder.find_event([post['text']], 0)
        # eventtext = post['text']
        if eventtext != "":
            y = find_year(dates, default_year)
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
    else:
        d = datefinder.find_dates_words(post['text'], dt.utcfromtimestamp(post['date']))
        if d is not None:
            date = datetime.date(year=d.year, month=d.month, day=d.day)
            eventtext = eventfinder.find_event([post['text']], 0)
            # eventtext = post['text']
            if eventtext != "":
                res.append((clean_vk_text(post['text']), date))
    return res


def clean_vk_text(text):
    pat1 = re.compile('\[.*?\|(.+?)]')
    m = pat1.findall(text)
    pat = re.compile('\[.*?\|.*?]')
    if m:
        #     found = m.groups()
        print(m)
        for g in m:
            text = pat.sub(g, text, 1)
    return text
