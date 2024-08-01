import datetime
import faulthandler
import sys
import time
from typing import Optional

import pm4py
from PyQt5.QtCore import QSize, QPoint, Qt, QSettings, QFile, QTextStream, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QSplitter, QVBoxLayout, QTableWidget, QTableWidgetItem, QWidget, \
    QHeaderView, QTabWidget, QAction, QFileDialog, QMessageBox
from graphviz import Digraph
from src.parsers.parse_petri_net import identify_patterns
from src.ui.ui_generic_elements import TransitionGraphicsItem
from src.ui.ui_petri_net_view import PetriNetEditorView
from src.utils.color_iterator import ColorIterator
from src.utils.petri_net_renderer import render_petri_net
from tests.parse_petri_net_test_file import online_order_petri_net


class CoolTransition(pm4py.PetriNet.Transition):
    def __init__(self, name: str):
        super().__init__(name)


def load_and_parse_petri_net() -> Digraph:
    net = online_order_petri_net()
    # net, im, fm = pm4py.read_pnml("model2012.pnml")

    seq, and_p, or_p = identify_patterns(net.places, net.transitions, net.arcs)

    color_iterator = ColorIterator()

    for pattern in seq:
        col: str = next(color_iterator)
        for elem in pattern:
            elem.properties["color"] = col

    return render_petri_net(net, False)


class TerminalView(QWidget):
    def __init__(self, columns: list[str]) -> None:
        super().__init__()
        self.columns = columns
        self.init_ui()

    def init_ui(self) -> None:
        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.table.setRowCount(0)
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)

        self.set_table_style()

    def set_table_style(self) -> None:
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("color: black; alternate-background-color: #f0f0f0; background-color: #ffffff;")

        font = QFont("Arial", 12, QFont.Bold)
        self.table.setFont(font)

        header_font = QFont("Arial", 14, QFont.Bold)
        self.table.horizontalHeader().setFont(header_font)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_row(self, data: list[str]) -> None:
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        for column, value in enumerate(data):
            self.table.setItem(row_position, column, QTableWidgetItem(value))

        self.table.scrollToBottom()


def open_and_parse_file(file_name: str) -> Optional[Digraph]:
    if file_name.endswith(".pnml"):
        net, im, fm = pm4py.read_pnml(file_name)
        return render_petri_net(net, False)


class PetriNetTab(QWidget):
    def __init__(self, current: int) -> None:
        super().__init__()

        if current == 0:
            self.init_editor(load_and_parse_petri_net())
        else:
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Petri Net File", "",
                                                       "Petri Net Files (*.pnml *.xml);;All Files (*)")
            if not file_name:
                raise FileNotFoundError("No file selected. Please select a valid Petri net file.")

            dot: Optional[Digraph] = open_and_parse_file(file_name)
            if dot is None:
                raise ValueError("Failed to parse Petri net file.")
            self.init_editor(dot)

    def init_editor(self, dot: Digraph) -> None:
        time.sleep(3)
        self.graph_view = PetriNetEditorView(dot)
        self.terminal_view = TerminalView(['Timestamp', 'CaseID', 'Activity'])

        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.graph_view)
        self.splitter.addWidget(self.terminal_view)
        self.splitter.setSizes([1080, 360])

        layout = QVBoxLayout(self)
        layout.addWidget(self.splitter)
        self.setLayout(layout)

        self.graph_view.scene.on_transition_fired.connect(self.on_transition_fired)

    @pyqtSlot(TransitionGraphicsItem)
    def on_transition_fired(self, transition: TransitionGraphicsItem) -> None:
        activity: str = transition.text_item.toPlainText() if transition.text_item else "No Activity"
        self.terminal_view.add_row([str(datetime.datetime.now()), "sfefwef", activity])


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Petri Net Editor")
        self.setGeometry(100, 100, 1920, 1080)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.settings = QSettings('petri_net_editor', 'pn_editor')

        self.resize(self.settings.value("size", QSize(1920, 1080)))
        self.move(self.settings.value("pos", QPoint(100, 100)))

        self.add_tab()

        self.init_menu()

    def init_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        new_tab_action = QAction('New Tab', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.add_tab)
        file_menu.addAction(new_tab_action)

    def add_tab(self) -> None:
        new_tab = PetriNetTab(self.tabs.count())
        self.tabs.addTab(new_tab, f"Tab {self.tabs.count() + 1}")

    def closeEvent(self, e) -> None:
        self.settings.setValue("size", self.size())
        self.settings.setValue("pos", self.pos())
        e.accept()


def main() -> None:
    app = QApplication(sys.argv)
    file = QFile(":/dark.qss")
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        app.setStyleSheet(stream.readAll())
    else:
        ...  # QMessageBox.warning(None, "Warning", "Failed to load stylesheet.")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
