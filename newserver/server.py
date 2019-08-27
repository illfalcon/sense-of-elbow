from flask import Flask
from .models import *
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    article = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False)
    approved = db.Column(db.Integer)
    event_date = db.Column(db.Date, nullable=False)


class Landing(db.Model):
    __tablename__ = "landings"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    type = db.Column(db.Integer)


class Webpage(db.Model):
    __tablename__ = "webpages"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False, default='')
    parsed = db.Column(db.Integer, nullable=False)
    # landing_id = db.Column(db.Integer, db.ForeignKey("landings.id"), nullable=False)


db.create_all()
import newcrawler.crawler

newcrawler.crawler.assess()


@app.route("/")
def index():
    flights = Webpage.query.all()
    return flights