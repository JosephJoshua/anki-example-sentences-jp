import aqt

from aqt import mw
from anki.notes import Note

ANKI21_VERSION = int(aqt.appVersion.split('.')[-1])

def get_config():
    return mw.addonManager.getConfig(__name__)

def get_note_type(note: Note) -> dict:
    if hasattr(note, 'note_type'):
        return note.note_type()
    else:
        return note.model()

def get_fields_from_note_type(note: Note) -> dict:
    if not config['fields']:
        return None

    note_type = get_note_type(note)['name']

    for fields in config['fields']:
        if fields['note_type'].lower() in note_type.lower():
            return fields

config = get_config()