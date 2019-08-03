from parser import extractor
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlsplit, urljoin
import html2text
import datetime
from utils.str import find_hash


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
        try:
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
                clean_text = html2text.html2text(r.text)
                h = find_hash(clean_text)
                old = db.get_url_hash(url)
                if old == h:
                    continue
                db.set_url_unparsed(url)
                db.set_url_hash(h, url)
                parse(r.text, url, db)
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
        except:
            continue
    db.drop_visited()


def parse(html, url, db):
    doc = extractor.parse_html(html)
    events = extractor.extract_events(doc)
    for e in events:
        eventtext = e[0]
        date = e[1]
        h = find_hash(eventtext)
        if not db.contains_event(h):
            db.add_event(eventtext, h, url, date)


def find_year(dates):
    year = 0
    for d in dates:
        if d.fact.year is not None:
            if d.fact.year > year:
                year = d.fact.year
    if year == 0:
        year = datetime.datetime.now().year
    return year
