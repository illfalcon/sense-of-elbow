import hashlib
from collections import deque


def find_hash(text):
    hash_obj = hashlib.sha1(text.encode())
    return hash_obj.hexdigest()


def remove_substrings(strings):
    queue = deque(sorted(strings, key=lambda s: len(s)))
    while len(queue) > 0:
        string = queue.popleft()
        for q in queue:
            if string in q:
                strings.remove(string)
                break


def remove_tuples(tuples):
    queue = deque(sorted(tuples, key=lambda t: len(t[0])))
    while len(queue) > 0:
        tup = queue.popleft()
        for q in queue:
            if tup[0] in q[0]:
                tuples.remove(tup)
                break
