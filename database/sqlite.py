import sqlite3
import datetime

from sqlite3 import Error


class Event:
    def __init__(self, rowid, url, article, event_date):
        self.rowid = rowid
        self.url = url
        self.article = article
        self.event_date = event_date


class MyDatabase:
    def __init__(self):
        self.con = None
        self.cursor_obj = None

    def sql_connection(self):
        try:
            self.con = sqlite3.connect('mydatabase.db', check_same_thread=False)
            self.cursor_obj = self.con.cursor()
        except Error:
            print(Error)

    def sql_create_tables(self):
        self.cursor_obj.execute(
            "CREATE TABLE IF NOT EXISTS landings (url TEXT NOT NULL, hash TEXT, name TEXT)"
        )
        self.cursor_obj.execute(
            "CREATE TABLE IF NOT EXISTS webpages (url TEXT NOT NULL, hash TEXT NOT NULL, parsed INTEGER NOT NULL)"
        )
        self.cursor_obj.execute(
            "CREATE TABLE IF NOT EXISTS events (url TEXT NOT NULL, hash TEXT NOT NULL, article TEXT NOT NULL, "
            "approved INTEGER, event_date TEXT)"
        )
        self.cursor_obj.execute(
            "CREATE TABLE IF NOT EXISTS users (login TEXT NOT NULL, password TEXT NOT NULL)"
        )
        self.con.commit()

    def start(self):
        self.sql_connection()
        self.sql_create_tables()

    def create_visited(self):
        self.cursor_obj.execute(
            "CREATE TABLE IF NOT EXISTS visited (url TEXT NOT NULL)"
        )
        self.con.commit()

    def visit_url(self, url):
        self.cursor_obj.execute(
            "INSERT into visited (url) VALUES (?)", (url, )
        )
        self.con.commit()

    def was_visited(self, url):
        self.cursor_obj.execute(
            "select count(*) from visited where url = ?", (url,)
        )
        res = self.cursor_obj.fetchone()[0]
        return res != 0

    def drop_visited(self):
        self.cursor_obj.execute(
            "DROP TABLE IF EXISTS visited"
        )
        self.con.commit()

    def add_landing(self, url, hash, name):
        self.cursor_obj.execute(
            "INSERT into landings (url, hash, name) VALUES (?, ?, ?)", (url, hash, name)
        )
        self.con.commit()

    def get_all_landings(self):
        self.cursor_obj.execute(
            "select url from landings"
        )
        rows = self.cursor_obj.fetchall()
        res = list(row[0] for row in rows)
        return res

    def add_url(self, url, hash):
        self.cursor_obj.execute(
            "INSERT into webpages (url, hash, parsed) VALUES (?, ?, ?)", (url, hash, 0)
        )
        self.con.commit()

    def contains_url(self, url):
        self.cursor_obj.execute(
            "select count(*) from webpages where url = ?", (url, )
        )
        res = self.cursor_obj.fetchone()[0]
        return res != 0

    def get_url_hash(self, url):
        self.cursor_obj.execute(
            "select hash from webpages where url = ?", (url, )
        )
        res = self.cursor_obj.fetchone()[0]
        return res

    def set_url_hash(self, hash, url):
        self.cursor_obj.execute(
            "update webpages set hash = ? where url = ?", (hash, url)
        )
        self.con.commit()

    def set_url_parsed(self, url):
        self.cursor_obj.execute(
            "update webpages set parsed = 1 where url = ?", (url, )
        )
        self.con.commit()

    def set_url_unparsed(self, url):
        self.cursor_obj.execute(
            "update webpages set parsed = 0 where url = ?", (url, )
        )
        self.con.commit()

    def add_event(self, text, hash, url, date):
        self.cursor_obj.execute(
            "INSERT into events (url, hash, article, event_date) values (?, ?, ?, ?)", (url, hash, text, date)
        )
        self.con.commit()

    # TODO: Add logic to check semantic similarity
    def contains_event(self, hash):
        self.cursor_obj.execute(
            "select count(*) from events where hash = ?", (hash, )
        )
        res = self.cursor_obj.fetchone()[0]
        return res != 0

    def get_unparsed_urls(self):
        self.cursor_obj.execute(
            "select url from webpages where parsed = 0"
        )
        rows = self.cursor_obj.fetchall()
        res = list(row[0] for row in rows)
        return res

    def get_user_by_login(self, login):
        self.cursor_obj.execute(
            "select * from users where login = ?", (login,)
        )
        res = self.cursor_obj.fetchone()
        if res is not None:
            return res[0], res[1]
        return None, None

    def get_relevant_events(self):
        n = datetime.datetime.now()
        year = n.year
        month = n.month
        day = n.day
        self.cursor_obj.execute(
            "select rowid, url, article, event_date from events where event_date >= ? and approved is null", (datetime.date(year, month, day),)
        )
        rows = self.cursor_obj.fetchall()
        res = []
        if rows is not None:
            for r in rows:
                res.append(Event(r[0], r[1], r[2], r[3]))
        return res

    def get_irrelevant_events(self):
        n = datetime.datetime.now()
        year = n.year
        month = n.month
        day = n.day
        self.cursor_obj.execute(
            "select rowid, url, article, event_date from events where event_date < ? and approved is null",
            (datetime.date(year, month, day),)
        )
        rows = self.cursor_obj.fetchall()
        res = []
        if rows is not None:
            for r in rows:
                res.append(Event(r[0], r[1], r[2], r[3]))
        return res

    def set_event_approved(self, rowid):
        self.cursor_obj.execute(
            "update events set approved = 1 where rowid = ?", (rowid,)
        )
        self.con.commit()

    def set_event_unapproved(self, rowid):
        self.cursor_obj.execute(
            "update events set approved = 0 where rowid = ?", (rowid,)
        )
        self.con.commit()

    def update_event_text(self, rowid, text):
        self.cursor_obj.execute(
            "update events set article = ? where rowid = ?", (text, rowid)
        )
        self.con.commit()

    def get_approved_events(self):
        self.cursor_obj.execute(
            "select rowid, url, article, event_date from events where approved == 1"
        )
        rows = self.cursor_obj.fetchall()
        res = []
        if rows is not None:
            for r in rows:
                res.append(Event(r[0], r[1], r[2], r[3]))
        return res

    def get_declined_events(self):
        self.cursor_obj.execute(
            "select rowid, url, article, event_date from events where approved == 0"
        )
        rows = self.cursor_obj.fetchall()
        res = []
        if rows is not None:
            for r in rows:
                res.append(Event(r[0], r[1], r[2], r[3]))
        return res
