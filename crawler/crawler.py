from parser import extractor
from ner import datefinder
from ner import eventfinder
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlsplit, urljoin
import hashlib
import html2text
import datetime
from calendar import monthrange

def is_webpage(url):
    try:
        r = requests.head(url, timeout=5)
        if 'content-type' in r.headers:
            if 'html' in r.headers['content-type']:
                return True
    except requests.exceptions.Timeout:
        print("request timed out: ", url)
        return False
    except requests.exceptions.RequestException as e:
        return False


def is_url_relevant(url, host):
    u = urlsplit(url)
    if (u.netloc == host) & (u.query == '') & (u.fragment == ''):
        return True
    return False


def crawl(depth, queue, db):
    db.create_visited()
    while len(queue) > 0:
        url, stage = queue.popleft()
        print(url, ' ', stage)
        if stage <= depth:
            # TODO: add if modified check
            if not db.contains_url(url):
                db.add_url(url, "")
            try:
                r = requests.get(url, allow_redirects=False, timeout=(30, 60))
            except requests.exceptions.Timeout:
                print("request timed out: ", url)
                continue
            except requests.exceptions.RequestException as e:
                print("exception occurred", e)
                continue
            text = r.text
            clean_text = html2text.html2text(text)
            h = find_hash(clean_text)
            old = db.get_url_hash(url)
            if old == h:
                continue
            db.set_url_unparsed(url)
            db.set_url_hash(h, url)
            parse(text, url, db)
            db.set_url_parsed(url)
            for link in BeautifulSoup(r.content, 'html.parser', parse_only=SoupStrainer('a')):
                if link.has_attr('href'):
                    new_url = urljoin(url, link['href'])
                    if not db.was_visited(new_url):
                        db.visit_url(new_url)
                        host = urlsplit(url).netloc
                        # if is_url_relevant(new_url, host) & is_webpage(new_url):
                        if is_url_relevant(new_url, host):
                            if is_webpage(new_url):
                                queue.append((new_url, stage + 1))
            # crawl(depth, queue, visited, db)
    db.drop_visited()


def parse(html, url, db):
    doc = extractor.parse_html(html)
    lines = doc.split('\n')
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
                h = find_hash(eventtext)
                if not db.contains_event(h):
                    db.add_event(eventtext, h, url, date)
                # print("line:\n", line, '\n')
                # print('event:')
                # print(eventtext, '\n', filtered_dates, '\n\n')


def find_hash(text):
    hash_obj = hashlib.sha1(text.encode())
    return hash_obj.hexdigest()


def find_year(dates):
    year = 0
    for d in dates:
        if d.fact.year is not None:
            if d.fact.year > year:
                year = d.fact.year
    if year == 0:
        year = datetime.datetime.now().year
    return year
