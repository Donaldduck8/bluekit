# coding:utf-8
import json
import traceback
from dataclasses import asdict

import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QStackedWidget, QVBoxLayout, QWidget
from qfluentwidgets import (InfoBar, InfoBarPosition, PrimaryPushButton,
                            SegmentedWidget, TextEdit, TitleLabel)

from .base_tree_frame import BaseFrame


class BaseTreeAndJsonEditWidget(QWidget):
    """ Base class for widgets with a pivot to switch between a custom view and a JSON editor. """

    def __init__(self, parent=None, title: str = '', data: dict = None):
        super().__init__(parent)
        self.setStyleSheet("""
            WidgetInterface{background: white}
            QTextEdit{
                font: 14px 'Segoe UI';
                border-radius: 8px;
                margin-top: 8px;
            }
        """)
        self.data = data
        self.resize(800, 600)
        self.setObjectName('widgetInterface' + str(id(self)))

        self.titleLabel = TitleLabel(title)
        self.titleLabel.setAlignment(PyQt5.QtCore.Qt.AlignCenter)

        self.pivot = SegmentedWidget(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addSpacing(10)

        self.custom_view = self.create_custom_view(parent=self, data=self.data)
        self.addSubInterface(self.custom_view, 'custom_view', 'Tree View')

        # JSON edit interface
        self.json_editor_frame = BaseFrame(parent=self)
        self.json_edit = TextEdit(parent=self)
        self.json_edit.setContentsMargins(0, 0, 0, 0)
        self.json_edit.setCurrentFont(PyQt5.QtGui.QFont('Helvetica', 10))
        self.json_edit.setText(json.dumps(self.data, default=asdict, indent=8))
        self.json_edit.setFontWeight(PyQt5.QtGui.QFont.Light)
        self.json_save_button = PrimaryPushButton(parent=self, text='Save')

        self.json_save_button.clicked.connect(self.update_data_from_json)

        self.json_editor_frame.addWidget(self.json_edit)
        self.json_editor_frame.addWidget(self.json_save_button)

        self.addSubInterface(self.json_editor_frame, 'json_edit', 'Editor')

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)
        self.vBoxLayout.setContentsMargins(30, 10, 30, 30)

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.custom_view)
        self.pivot.setCurrentItem(self.custom_view.objectName())

    def create_custom_view(self, parent, data):
        """ To be implemented in subclasses to create specific custom views. """
        raise NotImplementedError

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
        # Call update_data_from_json only if switching back to the custom view
        if widget == self.custom_view:
            self.update_data_from_json()

    def update_data_from_json(self):
        try:
            data_class = type(self.data)
            json_data = json.loads(self.json_edit.toPlainText())
            data = data_class(**json_data)
            self.data = data
            self.custom_view.update_data(data)
            InfoBar.success(
                title='Success!',
                content="JSON data has been successfully saved!",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
        except Exception:
            trace = traceback.format_exc()
            QMessageBox.critical(self, "Error", "Failed to parse JSON: " + trace)

    def on_execution_started(self):
        # Make JSON edit widget no longer available in stacked widget
        self.stackedWidget.removeWidget(self.json_editor_frame)
        self.pivot.removeWidget(self.json_editor_frame.objectName())
