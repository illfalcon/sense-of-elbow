import sqlite3

from sqlite3 import Error


class MyDatabase:
    def __init__(self):
        self.con = None
        self.cursor_obj = None

    def sql_connection(self):
        try:
            self.con = sqlite3.connect('mydatabase.db')
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
        self.con.commit()

    def start(self):
        self.sql_connection()
        self.sql_create_tables()

    def add_landing(self, url, hash, name):
        self.cursor_obj.execute(
            "INSERT into landings (url, hash, name) VALUES (?, ?, ?)", (url, hash, name)
        )
        self.con.commit()

    def get_all_landings(self):
        self.cursor_obj.execute(
            "select url from landings"
        )
        rows = self.cursor_obj.fetch_all()
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

    #TODO: Add logic to check semantic similarity
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
        rows = self.cursor_obj.fetch_all()
        res = list(row[0] for row in rows)
        return res


