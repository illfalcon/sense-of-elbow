# -*- coding: utf-8 -*-

from crawler import crawler
from collections import deque
from database.sqlite import MyDatabase

db = MyDatabase()
db.start()
depth = 2
urls = ["http://kdobru.ru/", "https://homeless.ru/news/",
        "https://xn----gtbbcgk3eei.xn--p1ai/o-nas/novosti-fonda", "https://hesed.spb.ru/news-3/"]
queue = deque([(url, 0) for url in urls])

crawler.crawl(depth, queue, db)
