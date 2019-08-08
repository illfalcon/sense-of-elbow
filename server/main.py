from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from .server import db
from crawler import crawler
from collections import deque
from multiprocessing import Process


main = Blueprint('main', __name__)
proc = Process()


@main.route('/')
def index():
    return redirect(url_for('main.new_events'))


@main.route('/new_events')
@login_required
def new_events():
    events = db.get_relevant_events()
    return render_template("events.html", events=sorted(events, key=lambda e: e.event_date), crawling=proc.is_alive())


@main.route('/past_events')
@login_required
def past_events():
    events = db.get_irrelevant_events()
    return render_template("events.html", events=sorted(events, key=lambda e: e.event_date, reverse=True), crawling=proc.is_alive())


@main.route('/approved_events')
@login_required
def approved_events():
    events = db.get_approved_events()
    return render_template("events.html", events=sorted(events, key=lambda e: e.event_date), crawling=proc.is_alive())


@main.route('/declined_events')
@login_required
def declined_events():
    events = db.get_declined_events()
    return render_template("events.html", events=sorted(events, key=lambda e: e.event_date), crawling=proc.is_alive())


@main.route('/approve_event', methods=['POST'])
@login_required
def approve_event():
    rowid = request.form.get('rowid')
    db.set_event_approved(rowid)
    return redirect(request.url)


@main.route('/decline_event', methods=['POST'])
@login_required
def decline_event():
    rowid = request.form.get('rowid')
    db.set_event_unapproved(rowid)
    return redirect(request.url)


@main.route('/add_landing', methods=['POST'])
@login_required
def add_landing():
    url = request.form.get('url')
    db.add_landing(url, "", "")
    return redirect(url_for('main.landings'))


@main.route('/delete_landing', methods=['POST'])
@login_required
def delete_landing():
    rowid = request.form.get('rowid')
    db.remove_landing(rowid)
    return redirect(url_for('main.landings'))


@main.route('/landings')
@login_required
def landings():
    landings = db.get_all_landings()
    return render_template("landings.html", landings=landings, crawling=proc.is_alive())


@main.route('/refresh', methods=['POST'])
@login_required
def refresh():
    global proc
    if not proc.is_alive():
        p = Process(target=start_crawling)
        p.start()
        proc = p
    return redirect(url_for('main.landings'))


def start_crawling():
    row_urls = db.get_all_landings()
    urls = list(u.url for u in row_urls)
    depth = 1
    queue = deque([(url, 0) for url in urls])
    crawler.crawl(depth, queue, db)
