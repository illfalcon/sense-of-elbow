# -*- coding: utf-8 -*-

from crawler import crawler
from collections import deque

depth = 2
url = "http://gaoordi.ru/news/"
visited = {url}
queue = deque([(url, 0)])

crawler.crawl(depth, queue, visited)