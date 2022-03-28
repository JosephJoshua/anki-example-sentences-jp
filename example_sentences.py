from bs4 import BeautifulSoup
import requests
import urllib.parse

YOUREI_URL = 'https://yourei.jp'

def get_sentences_from_page(soup: BeautifulSoup):
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

def get_example_sentences(word: str):
    word_escaped = urllib.parse.quote_plus(word.encode('utf-8'))

    page = requests.get(urllib.parse.urljoin(YOUREI_URL, word_escaped))
    soup = BeautifulSoup(page.content, 'html.parser')

    return get_sentences_from_page(soup)

def fill_note(note: Note, word_field: str, sentence_field: str):
    pass