from natasha import DatesExtractor
from datetime import datetime
from datetime import timedelta


def find_dates(text):
    extractor = DatesExtractor()
    matches = extractor(text)
    return matches


def find_dates_words(text, date):
    if 'послезавтра' in text.lower():
        return date + timedelta(days=2)
    if 'завтра' in text.lower():
        return date + timedelta()
    if 'сегодня' in text.lower():
        return date
    return None