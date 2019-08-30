from flask import Flask, make_response
from .models import *
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse
import datetime
from multiprocessing import Process
import json
from flask_cors import CORS
from utils.str import compare_passwords, random_string, find_hash


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


class Session(db.Model):
    __tablename__ = "sessions"
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("sessions"))
    expires = db.Column(db.DateTime, nullable=False)


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

    def to_dict(self):
        return {'id': self.id, 'url': self.url}


class Webpage(db.Model):
    __tablename__ = "webpages"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    hash = db.Column(db.String, nullable=False, default='')
    parsed = db.Column(db.Integer, nullable=False)
    # landing_id = db.Column(db.Integer, db.ForeignKey("landings.id"), nullable=False)


db.create_all()
import newcrawler.crawler


api = Api(app)


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp


class PastEventsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        n = datetime.datetime.now()
        year = n.year
        month = n.month
        day = n.day
        events = Event.query.filter(Event.event_date < datetime.date(year, month, day).strftime('%Y-%m-%d'), Event.approved == None).order_by(Event.event_date.desc()).limit(20).all()
        return {'events': [e.to_dict() for e in events]}, 200


class NewEventsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        n = datetime.datetime.now()
        year = n.year
        month = n.month
        day = n.day
        events = Event.query.filter(Event.event_date >= datetime.date(year, month, day).strftime('%Y-%m-%d'), Event.approved == None).order_by(Event.event_date).limit(20).all()
        return {'events': [e.to_dict() for e in events]}, 200


class ApprovedEventsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        events = Event.query.filter(Event.approved == 1).limit(20).all()
        return {'events': [e.to_dict() for e in events]}, 200


class DeclinedEventsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        events = Event.query.filter(Event.approved == 0).limit(20).all()
        return {'events': [e.to_dict() for e in events]}, 200


class SetApprovedResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        args = parser.parse_args()
        event = Event.query.get(args['id'])
        if not event:
            return {'success': False, 'error': 'event with id ' + str(args['id']) + 'not found'}, 404
        event.approved = 1
        db.session.commit()
        return {'success': True}, 200


class SetDeclinedResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        args = parser.parse_args()
        event = Event.query.get(args['id'])
        if not event:
            return {'success': False, 'error': 'event with id ' + str(args['id']) + 'not found'}, 404
        event.approved = 0
        db.session.commit()
        return {'success': True}, 200


class LandingsResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        landings = Landing.query.all()
        return {'landings': [l.to_dict() for l in landings]}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('url', type=str, required=True)
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        args = parser.parse_args()
        landing = Landing(url=args['url'].strip())
        db.session.add(landing)
        db.session.commit()
        return {'success': True, 'landing': landing.to_dict()}, 201

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        args = parser.parse_args()
        landing = Landing.query.get(args['id'])
        db.session.delete(landing)
        db.session.commit()
        return {'success': True}, 201


def check_auth_token(token):
    if not token:
        return None
    now = datetime.datetime.now()
    session = Session.query.get(token)
    if not session or now > session.expires:
        return None
    return session.user


class LoginResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = User.query.filter_by(login=args['login']).first()
        if not user:
            return {'success': False, 'error': 'user with login ' + args['login'] + ' not found'}, 404
        if not compare_passwords(args['password'], user.password):
            return {'success': False, 'error': 'wrong password'}, 400
        token = random_string(16)
        now = datetime.datetime.now()
        session = Session(id=token, user=user, expires=now+datetime.timedelta(days=+30))
        db.session.add(session)
        db.session.commit()
        return {'success': True, 'token': token}


class LoginTokenResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        return {'success': True}


class RegisterResource(Resource):
    def post(self):
        if len(User.query.all()) > 0:
            return {'success': False, 'error': 'number of users is above the limit already'}, 409
        parser = reqparse.RequestParser()
        parser.add_argument('login', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        args = parser.parse_args()
        user = User.query.filter_by(login=args['login']).first()
        if user:
            return {'success': False, 'error': 'user with login ' + args['login'] + ' already exists'}, 409
        password = find_hash(args['password'])
        login = args['login']
        newUser = User(login=login, password=password)
        db.session.add(newUser)
        db.session.commit()
        token = random_string(16)
        now = datetime.datetime.now()
        session = Session(id=token, user=newUser, expires=now + datetime.timedelta(days=+30))
        db.session.add(session)
        db.session.commit()
        return {'success': True, 'token': token}


class LogoutResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'you cannto perform this action'}, 401
        session = Session.query.get(args['Authentication'])
        if not session:
            return {'success': False, 'error': 'session not found'}, 404
        db.session.delete(session)
        db.session.commit()
        return {'success': True}


proc = Process()


class RenewResourse(Resource):
    def get(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('Authentication', type=str, location='headers')
        # args = parser.parse_args()
        # user = check_auth_token(args['Authentication'])
        # if not user:
        #     return {'success': False, 'error': 'Unauthorized access'}, 401
        return {'isRefreshing': proc.is_alive()}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authentication', type=str, location='headers')
        args = parser.parse_args()
        user = check_auth_token(args['Authentication'])
        if not user:
            return {'success': False, 'error': 'Unauthorized access'}, 401
        print('accepted request')
        global proc
        if not proc.is_alive():
            print('proc is not alive')
            p = Process(target=newcrawler.crawler.assess)
            p.start()
            print('process started')
            proc = p
            return {'success': True}, 200
        return {'success': False, 'error': 'Process is already running'}, 409


api.add_resource(PastEventsResource, '/api/past_events')
api.add_resource(NewEventsResource, '/api/new_events')
api.add_resource(ApprovedEventsResource, '/api/approved_events')
api.add_resource(DeclinedEventsResource, '/api/declined_events')
api.add_resource(SetApprovedResource, '/api/set_approved')
api.add_resource(SetDeclinedResource, '/api/set_declined')
api.add_resource(LandingsResource, '/api/landings')
api.add_resource(LoginResource, '/api/login')
api.add_resource(LogoutResource, '/api/logout')
api.add_resource(RegisterResource, '/api/register')
api.add_resource(LoginTokenResource, '/api/login_token')
api.add_resource(RenewResourse, '/api/renew')
