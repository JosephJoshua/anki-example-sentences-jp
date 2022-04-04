from typing import List
from bs4 import BeautifulSoup
import requests
import urllib.parse

from anki.collection import Collection
from anki.hooks import wrap
from anki.notes import Note
from anki.utils import htmlToTextLine
from aqt import mw

from .furigana import generate_furigana
from .utils import *

YOUREI_URL = 'https://yourei.jp'

def get_soup_instance(word: str):
    word_escaped = urllib.parse.quote_plus(word.encode('utf-8'))

    page = requests.get(urllib.parse.urljoin(YOUREI_URL, word_escaped))
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup

def get_first_sentence_from_page(soup: BeautifulSoup) -> str:
    sentence = soup.select_one('#sentence-1 > .the-sentence')

    if sentence is None:
        return '-'

    # Remove all the furigana from the text
    for furigana in sentence.find_all('rt'):
        furigana.decompose()

    return sentence.text

def get_all_sentences_from_page(soup: BeautifulSoup) -> List[str]:
    sentence_list = soup.select_one('.sentence-list')
    if sentence_list is None:
        return []

    sentence_items = sentence_list.find_all('li', {'class': 'clickable-sentence'}, recursive=False)
    if len(sentence_items) == 0:
        return []

    sentences = []
    for sentence in sentence_items:
        # Remove all the furigana from the text
        for furigana in sentence.find_all('rt'):
            furigana.decompose()

        the_sentence = sentence.select_one('.the-sentence')
        if the_sentence is None:
            continue

        sentences.append(the_sentence.text)

    return sentences

def can_fill_note(note: Note, word_field: str, sentence_field: str) -> bool:
    if not word_field or not sentence_field:
        return False

    if word_field not in note or sentence_field not in note:
        return False

    if not (mw.col.media.strip(note[word_field]).strip()):
        return False

    return True

# Adds the first example sentence we find to the note
def add_first_example_sentence(note: Note, word_field: str, sentence_field: str) -> bool:
    if not can_fill_note(note, word_field, sentence_field):
        return False

    if len(htmlToTextLine(note[sentence_field])) > 0:
        return False

    word = mw.col.media.strip(note[word_field])
    soup = get_soup_instance(word)

    sentence = get_first_sentence_from_page(soup)

    if should_auto_generate_furigana():
        sentence = generate_furigana(sentence)

    note[sentence_field] = sentence

    return True

def on_add_note(_col, note: Note, _deck_id):
    fields = get_fields_from_note_type(note)
    
    if fields is None:
        return

    if fields['auto_generate'] is not True:
        return

    word_field = fields['word']
    sentence_field = fields['sentence']

    add_first_example_sentence(note, word_field, sentence_field)

def init():
    Collection.add_note = wrap(Collection.add_note, on_add_note, 'before')