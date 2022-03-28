from typing import Sequence

from aqt import Collection, mw
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *

from .utils import *
from .example_sentences import fill_note

ACTION_NAME = 'Bulk-add Example Sentences'

def generate_sentences(selected_nids: Sequence, browser: Browser):
    note_count = len(selected_nids)

    def do(col: Collection):
        changed_notes = []

        note_count = len(selected_nids)
        note_index = 1

        for nid in selected_nids:
            note = col.get_note(nid)

            # TODO: Allow users to change the fields
            if fill_note(note, 'Front', 'Sentence'):
                changed_notes.append(note)

            # Update progress bar
            aqt.mw.taskman.run_on_main(
                lambda: aqt.mw.progress.update(
                    label=f"{note['Front']} ({note_index}/{note_count})",
                    value=note_index - 1,
                    max=note_count
                )
            )

            note_index += 1

        return col.update_notes(changed_notes)

    def show_success_dialog(_):
        dialog = QMessageBox()

        dialog.setContentsMargins(0, 5, 5, 5)
        dialog.setWindowTitle(ACTION_NAME)
        dialog.setText(f'Succesfully added example sentences for {note_count} notes')

        dialog.exec()

    operation = CollectionOp(parent=browser, op=do)
    operation.success(show_success_dialog)
    operation.run_in_background()

def setup_menu_items(browser: Browser):
    # Creates a menu item and adds it under the 'Edit' category
    action = QAction(ACTION_NAME, browser)
    qconnect(action.triggered, lambda: generate_sentences(browser.selected_notes(), browser))
    browser.form.menuEdit.addAction(action)

def init():
    if ANKI21_VERSION < 45:
        from anki.hooks import addHook
        addHook('browser.setupMenus', setup_menu_items)
    else:
        from aqt import gui_hooks
        gui_hooks.browser_menus_did_init.append(setup_menu_items)