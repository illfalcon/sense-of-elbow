from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, login, active=True):
        self.login = login
        self.active = active

    def is_active(self):
        # Here you should write whatever the code is
        # that checks the database if your user is active
        return self.active

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.login
