import newspaper
from parser import extractor
from urllib.parse import urlsplit, urljoin
import html2text
import datetime
from utils.str import find_hash
import magic
import vk
from newserver.server import *
import requests


def parse_vk(url):
    webpage = Webpage.query.filter_by(url=url).first()
    if not webpage:
        webpage = Webpage(url=url, parsed=False)
    session = vk.Session(access_token='ec103cffec103cffec103cffc5ec7c175deec10ec103cffb15ca3968351c46fffaf9426')
    vkapi = vk.API(session)
    dom = urlsplit(url).path
    posts = vkapi.wall.get(domain=dom[1:], v='5.100', count=20)['items']
    h = find_hash(posts[0]['text'])
    old = webpage.hash
    if old == h:
        print('unchanged')
        return
    webpage.parsed = 0
    webpage.hash = h
    for post in posts:
        print(post['text'])
        events = extractor.extract_events_from_vk(post)
        for e in events:
            eventtext = e[0]
            date = e[1]
            h = find_hash(eventtext)
            if len(Event.query.filter_by(hash=h).all()) == 0:
                db.session.add(Event(url=url, article=eventtext, hash=h, event_date=date))
                db.session.commit()
    webpage.parsed = 1
    db.session.commit()


def parse_newspaper(url):
    np = newspaper.build(url, language='ru', memoize_articles=False)
    for article in np.articles:
        if not Webpage.query.filter_by(url=article.url).first():
            page = Webpage(url=article.url, hash='', parsed=True)
            db.session.add(page)
            db.session.commit()
            article.download()
            article.parse()
            # print(article.url, article.text)
            text = extractor.normalize_newlines(article.text)
            events = extractor.extract_events_better_newspaper(text, article.url)
            for e in events:
                h = find_hash(e[0])
                if not Event.query.filter_by(hash=h).first():
                    e = Event(url=article.url, article=e[0], hash=h, event_date=e[1])
                    db.session.add(e)
                    db.session.commit()


def parse_page(url):
    page = Webpage.query.filter_by(url=url).first()
    if not page:
        page = Webpage(url=url, hash='', parsed=1)
        db.session.add(page)
        db.session.commit()
    try:
        r = requests.get(url, allow_redirects=False, timeout=(30, 60))
    except requests.exceptions.Timeout:
        print("request timed out: ", url)
        return
    except requests.exceptions.RequestException as e:
        print("exception occurred", e)
        return
    clean_text = html2text.html2text(r.text)
    h = find_hash(clean_text)
    old = page.hash
    if old == h:
        return
    page.hash = h
    db.session.commit()
    doc = extractor.parse_html(r.text)
    # events = extractor.extract_events(doc)
    events = extractor.extract_events_better(doc, url)
    for e in events:
        eventtext = e[0]
        date = e[1]
        h = find_hash(eventtext)
        if not Event.query.filter_by(hash=h).first():
            db.session.add(Event(article=eventtext, hash=h, url=url, event_date=date))
            db.session.commit()


def assess():
    landings = Landing.query.all()
    for landing in landings:
        if not landing.type:
            type = determine_type(landing)
            landing.type = type
            db.session.commit()
        if landing.type == 0:
            parse_newspaper(landing.url)
        elif landing.type == 2:
            parse_vk(landing.url)
        else:
            parse_page(landing.url)


def determine_type(landing):
    if urlsplit(landing.url).netloc == 'vk.com' or urlsplit(landing.url).netloc == 'vkontakte.ru':
        return 2
    elif len(newspaper.build(landing.url, memoize_articles=False).articles) > 0:
        return 0
    return 1
