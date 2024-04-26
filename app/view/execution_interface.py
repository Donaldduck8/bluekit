# coding:utf-8
# pylint: disable=E1101
import ctypes
import logging
import random
import sys
import threading
import time
import traceback

from PyQt5.QtCore import Qt, QTime, QTimer, pyqtSignal
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QHBoxLayout, QListWidgetItem, QVBoxLayout, QWidget
from qfluentwidgets import (Dialog, IndeterminateProgressRing, InfoBarIcon,
                            InfoBarPosition, SubtitleLabel, TitleLabel)
from qfluentwidgets.common.style_sheet import FluentStyleSheet, themeColor
from qfluentwidgets.components.widgets.list_view import ListWidget

from .. import installation_steps
from ..common.style_sheet import StyleSheet
from .base_frame import BaseFrame
from .listable_info_bar import InfoBar as ListableInfoBar


class ListWidgetLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget: ExecutionInterface = widget

    def emit(self, record):
        msg = self.format(record)

        # Maximum log length:
        self.widget.bottomListView.listWidget.remove_excess_items()

        # Maximum message length:
        if len(msg) > 1000:
            msg = msg[:1000] + '...'

        self.widget.bottomListView.listWidget.addItem(msg)
        self.widget.bottomListView.listWidget.scrollToBottom()


class ListFrame(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.listWidget = CustomListWidget(self)
        self.addWidget(self.listWidget)


class CustomListWidget(ListWidget):
    add_infobar_signal = pyqtSignal(str, str, InfoBarIcon)  # Signal to update the list widget safely

    def __init__(self, parent=None):
        super().__init__(parent)
        self.add_infobar_signal.connect(self.add_infobar)

        FluentStyleSheet.LIST_VIEW.apply(self)  # pylint: disable=no-member

        self.setContentsMargins(0, 400, 8, 4)
        self.setViewportMargins(0, 4, 0, 4)

    def add_infobar(self, title, content, icon):
        item = QListWidgetItem()

        infoBar = ListableInfoBar(
            icon=icon,
            title=title,
            content=content,
            orient=Qt.Vertical,
            isClosable=False,
            duration=-1,
            position=InfoBarPosition.NONE,
            parent=self
        )

        infoBar.titleLabel.setText(infoBar.title)

        infoBar.setMaximumWidth(self.width() - 2)
        infoBar.setFixedWidth(self.width() - 2)

        item.setSizeHint(infoBar.sizeHint())
        self.addItem(item)
        self.setItemWidget(item, infoBar)
        self.setSpacing(4)
        self.scrollToBottom()

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        for i in range(self.count()):
            widget = self.itemWidget(self.item(i))
            if not widget:
                continue

            widget.setMaximumWidth(self.width() - 2)
            widget.setFixedWidth(self.width() - 2)

    def remove_excess_items(self, max_items=30):
        while self.count() > max_items:
            self.takeItem(0)


class FluentTimer(QWidget):
    def __init__(self):
        super().__init__()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)

        self.label = SubtitleLabel("00:00", self)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.label)

        self.startTime = QTime(0, 0, 0)

    def start(self):
        self.timer.start(1000)

    def showTime(self):
        self.startTime = self.startTime.addSecs(1)

        if self.startTime.hour() > 0:
            self.label.setText(self.startTime.toString("hh:mm:ss"))
        else:
            self.label.setText(self.startTime.toString("mm:ss"))

    def stop(self):
        self.timer.stop()


class ExecutionInterface(QWidget):
    completion_signal = pyqtSignal()
    stop_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.completion_signal.connect(self.show_completion_dialog)
        self.stop_signal.connect(self.stop)

        self.setObjectName('executionInterface' + str(id(self)))

        # Main vertical layout
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)

        # Horizontal layout for the ProgressRing and the new ListWidget
        self.hBoxLayout = QHBoxLayout()

        self.topLeftLayout = QVBoxLayout()
        self.topLeftLayout.setContentsMargins(40, 20, 20, 40)

        self.progressRing = IndeterminateProgressRing(self)
        self.progressRing.setFixedSize(150, 150)

        self.topLeftLayout.addWidget(self.progressRing, alignment=Qt.AlignCenter | Qt.AlignVCenter)

        self.topLeftLayout.addSpacing(30)

        self.timerWidget = FluentTimer()
        self.topLeftLayout.addWidget(self.timerWidget, alignment=Qt.AlignCenter | Qt.AlignVCenter)

        self.hBoxLayout.addLayout(self.topLeftLayout)

        self.hBoxLayout.addSpacing(60)

        # New ListWidget to the right of the ProgressRing
        self.rightListView = ListFrame(self)
        self.rightListView.setMaximumHeight(250)
        self.rightListView.listWidget.setAutoScroll(True)

        self.hBoxLayout.addWidget(self.rightListView)

        self.hBoxLayout.setStretch(0, 0)

        # Add the horizontal layout to the main vertical layout
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addSpacing(60)

        self.bottomLabel = TitleLabel("Log")
        self.bottomLabel.setAlignment(Qt.AlignCenter)
        self.vBoxLayout.addWidget(self.bottomLabel)

        self.vBoxLayout.addSpacing(30)

        # Existing ListWidget at the bottom
        self.bottomListView = ListFrame(self)
        self.bottomListView.listWidget.setAutoScroll(True)

        # Add word wrap instead of cutting off the entry
        self.bottomListView.listWidget.setWordWrap(True)

        # Remove the spacing between element in the bottomListView
        self.bottomListView.listWidget.setSpacing(0)
        StyleSheet.CUSTOM_LIST_VIEW.apply(self.bottomListView.listWidget)

        self.vBoxLayout.addWidget(self.bottomListView)
        self.vBoxLayout.addSpacing(30)

    def execute(self, data: dict):
        self.timerWidget.startTime = QTime(0, 0, 0)
        self.timerWidget.start()

        log_handler = ListWidgetLogHandler(self)
        log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S',))
        installation_steps.logger.addHandler(log_handler)

        # check if we are frozen
        if getattr(sys, "frozen", False):
            thread = threading.Thread(target=threading_function, args=(self, data))
        else:
            thread = threading.Thread(target=threading_function_test, args=(self, data))
        thread.start()

    def show_completion_dialog(self):
        self.progressRing.setCustomBackgroundColor(themeColor(), themeColor())
        self.progressRing.stop()
        self.timerWidget.stop()

        title = 'Installation is complete!'
        content = """Some changes will only be applied after restarting your computer. Would you like to restart now?"""
        w = Dialog(title, content, self)
        w.show()
        w.setTitleBarVisible(False)

        if w.exec():
            w.close()
            installation_steps.restart()
        else:
            w.close()

    def stop(self):
        self.timerWidget.stop()
        self.progressRing.stop()


def threading_function_test(widget: ExecutionInterface, _data: dict):
    widget.timerWidget.startTime = QTime(1, 0, 0, 0)
    for _ in range(5):
        # widget.rightListView.listWidget.addItem("Item " + str(i))
        widget.rightListView.listWidget.add_infobar_signal.emit("Success: " + "word " * int(random.random() * 5), "", InfoBarIcon.SUCCESS)

        # Add a standard list item to the bottom list view
        widget.bottomListView.listWidget.addItem(QListWidgetItem("Lorem ipsum..."))
        widget.bottomListView.listWidget.scrollToBottom()
        widget.rightListView.listWidget.scrollToBottom()

        time.sleep(1)

    widget.stop_signal.emit()


def threading_function(widget: ExecutionInterface, data: dict):
    try:
        installation_steps.widget = widget
        installation_steps.install_bluekit(data, should_restart=False)

        widget.completion_signal.emit()
    except Exception as e:
        widget.rightListView.listWidget.add_infobar_signal.emit("Error", str(e), InfoBarIcon.ERROR)
        widget.bottomListView.listWidget.addItem(str(e))
        widget.stop_signal.emit()

        trace = traceback.format_exc()

        # Show message box
        ctypes.windll.user32.MessageBoxW(
            0,
            "A fatal exception occurred during installation. Please check the log for more information.\n\n" + trace,
            "Installation failed!",
            0x10,
        )

        widget.rightListView.listWidget.add_infobar_signal.emit("Error: " + trace, "", InfoBarIcon.ERROR)

        raise e
