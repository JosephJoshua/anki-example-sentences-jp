from aqt.operations import QueryOp
from aqt.qt import *
from PyQt5 import QtCore

from .example_sentences import get_soup_instance, get_all_sentences_from_page

_ACTION_NAME = 'Choose Example Sentence'

class ChooseExampleSentenceDialog(QDialog):
    sentence = ''

    def __init__(self, word: str, parent: QWidget = None):
        super().__init__(parent)

        self.word = word

        # Window icon
        self.window_icon = QIcon()
        self.window_icon.addPixmap(QPixmap(":/icons/anki.png"), QIcon.Normal, QIcon.Off)

        self.setWindowTitle(_ACTION_NAME)
        self.setWindowIcon(self.window_icon)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(16)

        # Heading text
        heading_font = QFont()
        heading_font.setPixelSize(18)

        self.heading = QLabel()
        self.heading.setText(_ACTION_NAME)
        self.heading.setFont(heading_font)
        self.heading.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.heading)

        # List view
        list_font = QFont()
        list_font.setFamily('Yu Gothic')
        list_font.setPixelSize(16)

        self.list_view = QListView()
        self.list_view.setViewportMargins(8, 8, 8, 8)
        self.list_view.setSpacing(4)
        self.list_view.setFont(list_font)
        self.list_view.setSelectionMode(QListView.SelectionMode.SingleSelection)

        self.list_model = self.load_list()
        self.list_view.setModel(self.list_model)

        self.layout.addWidget(self.list_view)

        # Button box
        buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(buttons)

        qconnect(self.button_box.accepted, self.accept)
        qconnect(self.button_box.rejected, self.reject)

        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)
        self.resize(720, 480)

    def load_list(self) -> QStandardItemModel:
        model = QStandardItemModel(self.list_view)

        def load_sentences(_):
            soup = get_soup_instance(self.word)
            self.sentences = get_all_sentences_from_page(soup)

        def load_model(_):
            for sentence in self.sentences:
                sentence_item = QStandardItem(sentence)
                sentence_item.setEditable(False)

                model.appendRow(sentence_item)

        QueryOp(parent=self.parent, op=load_sentences, success=load_model).with_progress(_ACTION_NAME).run_in_background()
        return model

    def accept(self):
        selected_indexes = self.list_view.selectedIndexes()

        if len(selected_indexes) == 0:
            QMessageBox.warning(self, _ACTION_NAME, 'Please select an example sentence to add')
            return

        self.sentence = selected_indexes[0].data()
        super().accept()

    def reject(self):
        super().reject()
