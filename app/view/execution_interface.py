# coding:utf-8
from ..common.style_sheet import StyleSheet

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame, QListWidgetItem
from qfluentwidgets import (FluentIcon, ProgressRing, InfoBar, ProgressBar, ScrollArea, ListWidget)


class ExecutionInterface(QWidget):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        self.setObjectName('executionInterface' + str(id(self)))

        # Main vertical layout
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)

        # Horizontal layout for the ProgressRing and the new ListWidget
        self.hBoxLayout = QHBoxLayout()

        # ProgressRing configuration
        self.progressRing = ProgressRing(self)
        self.progressRing.setValue(0)
        self.progressRing.setTextVisible(True)
        self.hBoxLayout.setContentsMargins(70, 30, 70, 0)
        self.hBoxLayout.addWidget(self.progressRing, alignment=Qt.AlignLeft)
        self.hBoxLayout.addSpacing(60)

        # New ListWidget to the right of the ProgressRing
        self.rightListView = ListWidget(self)
        self.rightListView.setMaximumHeight(150)
        for _ in range(10):  # Adjust the number of items as needed
            self.rightListView.addItem(QListWidgetItem("Right Panel Item"))
        self.hBoxLayout.addWidget(self.rightListView, alignment=Qt.AlignRight)

        self.hBoxLayout.setStretch(0, 0)

        # Add the horizontal layout to the main vertical layout
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.vBoxLayout.addSpacing(100)

        # Existing ListWidget at the bottom
        self.bottomListView = ListWidget(self)
        for _ in range(100):  # Adjust the number of items as needed
            self.bottomListView.addItem(QListWidgetItem("Bottom Panel Item"))
        self.vBoxLayout.addWidget(self.bottomListView)
