from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from .server import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return redirect(url_for('main.events'))


@main.route('/events')
@login_required
def events():
    return render_template("events.html")


@main.route('/landings')
@login_required
def landings():
    return render_template("landings.html")

@main.route('/relevant_events')
@login_required
def relevant_events():
    return db.get_relevant_events()