# -*- coding: utf-8 -*-

from crawler import crawler
from collections import deque
from database.sqlite import MyDatabase

db = MyDatabase()
db.start()
depth = 2
url = "http://kdobru.ru/"
visited = {url}
queue = deque([(url, 0)])

crawler.crawl(depth, queue, visited, db)
