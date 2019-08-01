from parser import extractor
from ner import datefinder
from ner import eventfinder
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlsplit, urljoin
import hashlib


def is_webpage(url):
    r = requests.head(url)
    if 'content-type' in r.headers:
        if 'html' in r.headers['content-type']:
            return True
    return False


def is_url_relevant(url, host):
    u = urlsplit(url)
    if (u.netloc == host) & (u.query == '') & (u.fragment == ''):
        return True
    return False


def crawl(depth, queue, visited, db):
    if len(queue) > 0:
        url, stage = queue.popleft()
        print(url, ' ', stage)
        if stage <= depth:
            r = requests.get(url)
            text = r.text
            parse(text)
            for link in BeautifulSoup(r.content, 'html.parser', parse_only=SoupStrainer('a')):
                if link.has_attr('href'):
                    new_url = urljoin(url, link['href'])
                    if new_url not in visited:
                        visited.add(new_url)
                        host = urlsplit(url).netloc
                        # if is_url_relevant(new_url, host) & is_webpage(new_url):
                        if is_url_relevant(new_url, host):
                            if is_webpage(new_url):
                                queue.append((new_url, stage + 1))
            crawl(depth, queue, visited)



def parse(html):
    doc = extractor.parse_html(html)
    lines = doc.split('\n')
    for i, line in enumerate(lines):
        dates = datefinder.find_dates(line)
        filtered_dates = list(filter(lambda d: (d.fact.day is not None) & (d.fact.month is not None), dates))
        if len(filtered_dates) != 0:
            eventtext = eventfinder.find_event(lines, i)
            if eventtext != "":
                print("line:\n", line, '\n')
                print('event:')
                print(eventtext, '\n', filtered_dates, '\n\n')


def find_hash(text):
    hash_obj = hashlib.md5(text.encode())
    return hash_obj.hexdigest()
