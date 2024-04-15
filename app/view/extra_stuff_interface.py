# coding:utf-8
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout

import json5.host
from ..common.style_sheet import StyleSheet
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QFrame, QListWidgetItem

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget, QMessageBox)
from qfluentwidgets import SegmentedWidget, TextEdit, ListWidget
from qfluentwidgets import FluentIcon as FIF

import PyQt5
import json5


class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 8, 0, 0)

        self.setObjectName('frame')
        StyleSheet.VIEW_INTERFACE.apply(self)

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)


class ListFrame(Frame):

    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)

        self.data = data

        self.list = ListWidget(self)
        self.addWidget(self.list)

        # Make first column expand to fit
        self.setContentsMargins(50, 30, 50, 30)

        # Add a border around self.tree
        self.setMinimumWidth(800)

    def clear(self):
        self.list.clear()

    def addItem(self, item: QListWidgetItem):
        item = QListWidgetItem(item)
        item.icon = FIF.PIN
        item.setBackground(QColor(167, 199, 231, 60))
        self.list.addItem(item)

class ExtraStuffInterface(QWidget):
    def __init__(self, parent=None, data: dict = None):
        super().__init__(parent)
        self.setStyleSheet("""
            ScoopInterface{background: white}
            QTextEdit{
                font: 14px 'Segoe UI';
                border-radius: 8px;
            }
        """)

        self.data = data
        self.resize(800, 600)
        self.setObjectName('extra_stuff_interface' + str(id(self)))

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.list_view = ListFrame(parent=self, data=self.data)
        self.addSubInterface(self.list_view, 'list', 'List View')

        # JSON edit interface
        self.json_edit = TextEdit(parent=self)
        self.json_edit.setCurrentFont(PyQt5.QtGui.QFont('Helvetica', 10))
        self.json_edit.setText(json5.dumps(self.data, indent=8, sort_keys=True))
        self.json_edit.setFontWeight(PyQt5.QtGui.QFont.Light)
        # self.json_edit.setPlainText()
        self.addSubInterface(self.json_edit, 'json_edit', 'JSON Edit')

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.list_view)
        self.pivot.setCurrentItem(self.list_view.objectName())

        self.update_data_from_json()

    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget),
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())
        # Call update_data_from_json only if switching back to the tree view
        if widget == self.list_view:
            self.update_data_from_json()

    def update_data_from_json(self):
        try:
            data = json5.loads(self.json_edit.toPlainText())
            self.list_view.clear()
            for url in data:
                self.list_view.addItem(url)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to parse JSON: " + str(e))