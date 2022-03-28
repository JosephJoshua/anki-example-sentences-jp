from typing import Sequence

from aqt import mw
from aqt.qt import *
from aqt.browser import Browser

from .utils import *

ACTION_NAME = 'Bulk-add Example Sentences'

def generate_sentences(selected_nids: Sequence):
    mw.checkpoint(ACTION_NAME)
    mw.progress.start()

    for nid in selected_nids:
        note = mw.col.get_note(nid)

    mw.progress.finish()
    mw.reset()

def setup_menu_items(browser: Browser):
    # Creates a menu item and adds it under the 'Edit' category
    action = QAction(ACTION_NAME, browser)
    qconnect(action.triggered, lambda: generate_sentences(browser.selected_notes()))
    browser.form.menuEdit.addAction(action)

def init():
    if ANKI21_VERSION < 45:
        from anki.hooks import addHook
        addHook('browser.setupMenus', setup_menu_items)
    else:
        from aqt import gui_hooks
        gui_hooks.browser_menus_did_init.append(setup_menu_items)