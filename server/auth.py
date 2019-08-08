from flask import Blueprint, render_template, request, redirect, url_for, flash
from .server import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template("login.html")


@auth.route('/login', methods=['POST'])
def login_post():
    login = request.form.get('login')
    password = request.form.get('password')
    if not login or not password:
        flash('Проверьте введённые данные и попробуйте снова.')
        return redirect(url_for('auth.login'))
    res_login, res_password = db.get_user_by_login(login)
    if not res_login or not res_password or res_password != password:
        flash('Проверьте введённые данные и попробуйте снова.')
        return redirect(url_for('auth.login'))
    login_user(User(res_login), remember=True)
    return redirect(url_for('main.new_events'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.new_events'))
