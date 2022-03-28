from typing import List
from bs4 import BeautifulSoup
import requests
import urllib.parse

from aqt import mw
from anki.notes import Note
from anki.utils import htmlToTextLine

YOUREI_URL = 'https://yourei.jp'

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

def get_first_sentence_from_page(soup: BeautifulSoup) -> str:
    sentence = soup.select_one('#sentence-1 > .the-sentence')

    if sentence is None:
        return '-'

    # Remove all the furigana from the text
    for furigana in sentence.find_all('rt'):
        furigana.decompose()

    return sentence.text

def get_soup_instance(word: str):
    word_escaped = urllib.parse.quote_plus(word.encode('utf-8'))

    page = requests.get(urllib.parse.urljoin(YOUREI_URL, word_escaped))
    soup = BeautifulSoup(page.content, 'html.parser')

    return soup

def can_fill_note(note: Note, word_field: str, sentence_field: str) -> bool:
    if not word_field or not sentence_field:
        return False

    if word_field not in note or sentence_field not in note:
        return False

    if not (mw.col.media.strip(note[word_field]).strip()):
        return False

    # Should only fill the note if the sentence field is still empty
    # TODO: Add support for changing the example sentences of a note
    if len(htmlToTextLine(note[sentence_field])) == 0:
        return True

    return False

def fill_note(note: Note, word_field: str, sentence_field: str) -> bool:
    if not can_fill_note(note, word_field, sentence_field):
        return False

    word = mw.col.media.strip(note[word_field])
    soup = get_soup_instance(word)

    sentence = get_first_sentence_from_page(soup)
    note[sentence_field] = sentence

    return True