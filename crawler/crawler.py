from parser import extractor
import requests
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlsplit, urljoin
import html2text
import datetime
from utils.str import find_hash
import magic
import vk


def is_webpage(url):
    try:
        m = ''
        r = requests.get(url, timeout=5, stream=True)
        for chunk in r.iter_content(chunk_size=100):
            m = magic.from_buffer(chunk, mime=True)
            break
        if 'html' in m:
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


# def is_landing_page(url, db):
#     event_pages = list()
#     try:
#         r = requests.get(url, allow_redirects=False, timeout=(30, 60))
#     except requests.exceptions.Timeout:
#         print("request timed out: ", url)
#         return
#     except requests.exceptions.RequestException as e:
#         print("exception occurred", e)
#         return
#     links = BeautifulSoup(r.content, 'html.parser', parse_only=SoupStrainer('a'))
#     for link in list(links)[0:51]:
#         if link.has_attr('href'):
#             new_url = urljoin(url, link['href'])
#             host = urlsplit(url).netloc
#             if is_url_relevant(new_url, host):
#                 if is_webpage(new_url):
#                     try:
#                         req = requests.get(new_url, allow_redirects=False, timeout=(30, 60))
#                     except requests.exceptions.Timeout:
#                         print("request timed out: ", url)
#                         continue
#                     except requests.exceptions.RequestException as e:
#                         print("exception occurred", e)
#                         continue
#                     events = parse_with_no_db(req.text, new_url)
#                     if len(events) > 0:
#                         event_pages.append(new_url)
#     if len(event_pages) >= len(links)/3:
#         return True
#     return False


def parse_vk(url, db):
    session = vk.Session(access_token='ec103cffec103cffec103cffc5ec7c175deec10ec103cffb15ca3968351c46fffaf9426')
    vkapi = vk.API(session)
    dom = urlsplit(url).path
    posts = vkapi.wall.get(domain=dom[1:], v='5.100', count=20)['items']
    h = find_hash(posts[0]['text'])
    old = db.get_url_hash(url)
    if old == h:
        print('unchanged')
        return
    db.set_url_unparsed(url)
    db.set_url_hash(h, url)
    for post in posts:
        events = extractor.extract_events_from_vk(post)
        for e in events:
            eventtext = e[0]
            date = e[1]
            h = find_hash(eventtext)
            if not db.contains_event(h):
                db.add_event(eventtext, h, url, date)
    db.set_url_parsed(url)


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
                if urlsplit(url).netloc == 'vk.com' or urlsplit(url).netloc == 'vkontakte.ru':
                    parse_vk(url, db)
                    continue
                try:
                    r = requests.get(url, allow_redirects=False, timeout=(30, 60))
                except requests.exceptions.Timeout:
                    print("request timed out: ", url)
                    continue
                except requests.exceptions.RequestException as e:
                    print("exception occurred", e)
                    continue
                clean_text = html2text.html2text(r.text)
                # print(r.text)
                h = find_hash(clean_text)
                old = db.get_url_hash(url)
                if old == h:
                    continue
                db.set_url_unparsed(url)
                db.set_url_hash(h, url)
                parse(r.text, url, db)
                db.set_url_parsed(url)
                links = BeautifulSoup(r.content, 'html.parser', parse_only=SoupStrainer('a'))
                for link in list(links)[:51]:
                    if link.has_attr('href'):
                        new_url = urljoin(url, link['href'])
                        if not db.was_visited(new_url):
                            db.visit_url(new_url)
                            host = urlsplit(url).netloc
                            # if is_url_relevant(new_url, host) & is_webpage(new_url):
                            if is_url_relevant(new_url, host):
                                if is_webpage(new_url):
                                    queue.append((new_url, stage + 1))
        except Exception as e:
            print(e)
            continue
    db.drop_visited()


# def parse_with_no_db(html, url):
#     doc = extractor.parse_html(html)
#     # events = extractor.extract_events(doc)
#     events = extractor.extract_events_better(doc, url)
#     return events


def parse(html, url, db):
    doc = extractor.parse_html(html)
    # events = extractor.extract_events(doc)
    events = extractor.extract_events_better(doc, url)
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
