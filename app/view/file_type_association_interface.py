# coding:utf-8
from PyQt5.QtWidgets import QWidget, QVBoxLayout

import json5.host
from .base_tree_frame import BaseTreeFrame
from PyQt5.QtWidgets import QWidget, QTreeWidgetItem

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget, QMessageBox)
from qfluentwidgets import SegmentedWidget, TextEdit, TitleLabel

import PyQt5
import json5


class TreeFrame(BaseTreeFrame):
    def __init__(self, parent=None, data: dict = None):
        headers = ["Name", "Arguments"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def update_data(self, data: dict):
        self.tree.clear()  # Clear the existing items
        self.data = data
        self.populate_tree()

    def populate_tree(self):
        if not isinstance(self.data, dict):
            return

        for category, value in self.data.items():
            if not isinstance(value, dict):
                continue

            category_item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(category_item)

            entry_item = QTreeWidgetItem([value["program_name"], " ".join(value["arguments"])])
            category_item.addChild(entry_item)

            file_types_item = QTreeWidgetItem(["File Types"])
            entry_item.addChild(file_types_item)

            for file_extension in value["file_types"]:
                file_types_item.addChild(QTreeWidgetItem(["." + file_extension]))

        self.tree.expandAll()

    def populate_tree_item(self, parent_item, items):
        for sub_item in items:
            if isinstance(sub_item, tuple) and len(sub_item) == 3:
                parent_item.addChild(QTreeWidgetItem([sub_item[1], sub_item[2]]))
            elif isinstance(sub_item, dict) and sub_item.get("type") == "one_of":
                main_item = QTreeWidgetItem([sub_item["main"][1], sub_item["main"][2]])
                alt_item = QTreeWidgetItem([sub_item["alternative"][1], sub_item["alternative"][2]])
                parent_item.addChild(main_item)
                main_item.addChild(alt_item)
        self.tree.expandAll()


class FTAInterface(QWidget):
    """ Home interface with a pivot to switch between tree view and a JSON editor. """

    def __init__(self, parent=None, title: str = '', data: dict = None):
        super().__init__(parent)
        self.setStyleSheet("""
            ScoopInterface{background: white}
            QTextEdit{
                font: 14px 'Segoe UI';
                border-radius: 8px;
                margin-top: 8px;
            }
        """)
        self.data = data
        self.resize(800, 600)
        self.setObjectName('ftaInterface' + str(id(self)))

        self.titleLabel = TitleLabel(title)
        self.titleLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)
        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(10)

        # Tree view interface
        self.tree_view = TreeFrame(parent=self, data=self.data)
        self.addSubInterface(self.tree_view, 'tree_view', 'Tree View')

        # JSON edit interface
        self.json_edit = TextEdit(parent=self)
        self.json_edit.setCurrentFont(PyQt5.QtGui.QFont('Helvetica', 10))
        self.json_edit.setText(json5.dumps(self.data, indent=8, sort_keys=True))
        self.json_edit.setFontWeight(PyQt5.QtGui.QFont.Light)

        # self.json_edit.setPlainText()
        self.addSubInterface(self.json_edit, 'json_edit', 'Editor')

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.tree_view)
        self.pivot.setCurrentItem(self.tree_view.objectName())

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
        if widget == self.tree_view:
            self.update_data_from_json()

    def update_data_from_json(self):
        try:
            data = json5.loads(self.json_edit.toPlainText())
            self.tree_view.update_data(data)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to parse JSON: " + str(e))
