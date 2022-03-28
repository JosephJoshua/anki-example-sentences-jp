from typing import Sequence

from aqt import Collection
from aqt.browser import Browser
from aqt.operations import CollectionOp
from aqt.qt import *

from .utils import *
from .example_sentences import fill_note

ACTION_NAME = 'Bulk-add Example Sentences'

def show_confirmation_dialog(note_count: int, browser: Browser):
    reply = QMessageBox.question(browser, ACTION_NAME, f'Are you sure you want to generate example sentences for {note_count} notes?')
    return reply == QMessageBox.StandardButton.Yes

def show_success_dialog(note_count: int):
    dialog = QDialog()

    # Layout
    layout = QVBoxLayout()

    layout.setContentsMargins(16, 16, 16, 16)
    layout.setSpacing(8)

    # Message
    message = QLabel()
    message.setText(f'Succesfully added example sentences for {note_count} notes')

    layout.addWidget(message)

    # Button box
    button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    qconnect(button_box.accepted, lambda: dialog.reject())

    layout.addWidget(button_box)

    # Window icon
    icon = QIcon()
    icon.addPixmap(QPixmap(":/icons/anki.png"), QIcon.Normal, QIcon.Off)

    dialog.setWindowTitle(ACTION_NAME)
    dialog.setWindowIcon(icon)
    dialog.setLayout(layout)
    dialog.exec()

def generate_sentences(selected_nids: Sequence, browser: Browser):
    note_count = len(selected_nids)
    if not show_confirmation_dialog(note_count, browser):
        return

    def do(col: Collection):
        changed_notes = []
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
                    value=note_index,
                    max=note_count
                )
            )

            note_index += 1

        return col.update_notes(changed_notes)

    operation = CollectionOp(parent=browser, op=do)
    operation.success(lambda _: show_success_dialog(note_count))
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