from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from .server import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.new_events'))


@main.route('/new_events')
@login_required
def new_events():
    events = db.get_relevant_events()
    return render_template("events.html", events=events)


@main.route('/past_events')
@login_required
def past_events():
    events = db.get_irrelevant_events()
    return render_template("events.html", events=events)


@main.route('/landings')
@login_required
def landings():
    return render_template("landings.html")
