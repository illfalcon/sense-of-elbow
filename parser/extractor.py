from readability import Document
import html2text
import re


def normalize_newlines(text):
    text = re.sub("\n+", "\n", text)
    return text


def parse_html(html_text):
    doc = Document(html_text)
    h = html2text.HTML2Text()
    h.ignore_links = True
    h.ignore_tables = True
    h.emphasis_mark = ''
    h.strong_mark = ''
    h.ignore_images = True
    h.unicode_snob = True
    h.body_width = 0
    h.wrap_links = False
    try:
        return normalize_newlines(doc.title() + '\n' + h.handle(doc.summary()))
    except:
        return ""
