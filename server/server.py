from flask import Flask
from config import Config
from database.sqlite import MyDatabase
from .models import *
from flask_login import LoginManager
from .login_models import User
from flask_cors import CORS
import newcrawler.crawler

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
database = SQLAlchemy(app)
database.create_all()
print(Landing.query.all())


# db = MyDatabase()
# db.start()

# login_manager = LoginManager()
# login_manager.login_view = 'auth.login'
# login_manager.init_app(app)


# @login_manager.user_loader
# def load_user(login):
#     user_login, _ = db.get_user_by_login(login)
#     return User(login)


# from .auth import auth as auth_blueprint
# app.register_blueprint(auth_blueprint)
#
#
# from .main import main as main_blueprint
# app.register_blueprint(main_blueprint)
