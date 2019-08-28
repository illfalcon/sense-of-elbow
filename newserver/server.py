from flask import Flask, make_response, jsonify
from .models import *
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api
import datetime
import json

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

    def to_dict(self):
        return {'id': self.id, 'url': self.url, 'article': self.article, "event_date": self.event_date.strftime('%d-%m-%Y')}


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

# newcrawler.crawler.assess()


api = Api(app)


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp


class PastEventsResource(Resource):
    def get(self):
        n = datetime.datetime.now()
        year = n.year
        month = n.month
        day = n.day
        events = Event.query.filter(Event.event_date < datetime.date(year, month, day).strftime('%d-%m-%Y'), Event.approved == None).limit(20).all()
        return {'events': [e.to_dict() for e in events]}, 200


api.add_resource(PastEventsResource, '/api/past_events')
