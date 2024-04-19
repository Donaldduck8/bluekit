# coding:utf-8
import json5
import json5.host
import PyQt5
from PyQt5.QtWidgets import (QMessageBox, QStackedWidget,
                             QTreeWidgetItem, QVBoxLayout, QWidget)
from qfluentwidgets import SegmentedWidget, TextEdit, TitleLabel

from .base_tree_frame import BaseTreeFrame

class RegistryChangesTreeFrame(BaseTreeFrame):
    def __init__(self, parent=None, data: dict = None):
        headers = ["Name", "Value", "Type", "Data"]
        super().__init__(parent, headers, data)
        self.update_data(data)

    def update_data(self, data: dict):
        self.tree.clear()  # Clear the existing items
        self.data = data
        self.populate_tree()

    def populate_tree(self):
        for category, items in self.data.items():
            category_item = QTreeWidgetItem([category])
            self.tree.addTopLevelItem(category_item)
            self.populate_tree_item(category_item, items)
        
        self.tree.expandAll()

    def populate_tree_item(self, parent_item, items):
        for item in items:
            details = [
                item.get('description', ''),
                item.get('value', ''),
                item.get('type', ''),
                item.get('data', '')
            ]
            child_item = QTreeWidgetItem(details)
            parent_item.addChild(child_item)


class RegistryChangesWidget(QWidget):
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
        
        self.data = json5.loads(json5.dumps(data, sort_keys=True))
        self.resize(800, 600)
        self.setObjectName('scoopInterface' + str(id(self)))

        self.titleLabel = TitleLabel(title)
        self.titleLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(10)

        # Tree view interface
        self.tree_view = RegistryChangesTreeFrame(parent=self, data=self.data)
        self.addSubInterface(self.tree_view, 'tree_view', 'Tree View')

        # JSON edit interface
        self.json_edit = TextEdit(parent=self)
        self.json_edit.setContentsMargins(0, 80000, 0, 0)
        self.json_edit.setCurrentFont(PyQt5.QtGui.QFont('Helvetica', 10))
        self.json_edit.setText(json5.dumps(self.data, indent=8, sort_keys=True))
        self.json_edit.setFontWeight(PyQt5.QtGui.QFont.Light)
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
