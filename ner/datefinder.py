from natasha import DatesExtractor


def find_dates(text):
    extractor = DatesExtractor()
    matches = extractor(text)
    return matches
