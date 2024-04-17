# coding:utf-8
import logging
import threading

from PyQt5.QtCore import (Qt,
                          pyqtSignal, QTime, QTimer)
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import (QHBoxLayout,
                             QListWidgetItem, QVBoxLayout, QWidget)
from qfluentwidgets import (FluentStyleSheet,
                            IndeterminateProgressRing, InfoBarIcon,
                            InfoBarPosition, ListWidget, TitleLabel)
from qfluentwidgets.common.style_sheet import FluentStyleSheet, themeColor
from qfluentwidgets.components.widgets.list_view import ListWidget
from qfluentwidgets import SubtitleLabel, Dialog

from .. import installation_steps, utils
from ..common.style_sheet import StyleSheet
from .base_frame import BaseFrame
from .listable_info_bar import InfoBar as ListableInfoBar


class ListWidgetLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
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
        # self.setWordWrap(True)
        self.add_infobar_signal.connect(self.add_infobar)

        FluentStyleSheet.LIST_VIEW.apply(self)

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
        self.scrollToBottom()

    def resizeEvent(self, e: QResizeEvent) -> None:
        super().resizeEvent(e)
        for i in range(self.count()):
            widget = self.itemWidget(self.item(i))
            if not widget:
                continue

            widget.setMaximumWidth(self.width() - 2)
            widget.setFixedWidth(self.width() - 2)


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
        self.label.setText(self.startTime.toString("mm:ss"))

    def stop(self):
        self.timer.stop()


class ExecutionInterface(QWidget):
    completion_signal = pyqtSignal()

    def __init__(self, parent=None, title=None):
        super().__init__(parent)

        self.completion_signal.connect(self.show_completion_dialog)

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

        # Add word wrap instead of cutting off the entry
        self.bottomListView.listWidget.setWordWrap(True)

        # Remove the spacing between element in the bottomListView
        self.bottomListView.listWidget.setSpacing(0)
        StyleSheet.CUSTOM_LIST_VIEW.apply(self.bottomListView.listWidget)

        self.vBoxLayout.addWidget(self.bottomListView)
        self.vBoxLayout.addSpacing(30)

    def execute(self, data):
        self.timerWidget.startTime = QTime(0, 0, 0)
        self.timerWidget.start()

        log_handler = ListWidgetLogHandler(self)
        log_handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S',))
        installation_steps.logger.addHandler(log_handler)

        # check if we are frozen
        import sys
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
        content = """Some changes (like taskbar pins) will only be applied after restarting your computer. Would you like to restart now?"""
        w = Dialog(title, content, self)
        w.show()
        w.setTitleBarVisible(False)
        # w.setContentCopyable(True)
        if w.exec():
            w.close()
            installation_steps.restart()
        else:
            w.close()


def threading_function_test(widget: ExecutionInterface, data: dict):
    for i in range(5):
        import time
        import random

        # widget.rightListView.listWidget.addItem("Item " + str(i))
        widget.rightListView.listWidget.add_infobar_signal.emit("Success: " + "word " * int(random.random() * 21), "", InfoBarIcon.SUCCESS)

        # Add a standard list item to the bottom list view
        widget.bottomListView.listWidget.addItem(QListWidgetItem("Item " + str(i)))
        widget.bottomListView.listWidget.scrollToBottom()
        widget.rightListView.listWidget.scrollToBottom()

        time.sleep(1)

    widget.completion_signal.emit()


def threading_function(widget: ExecutionInterface, data: dict):
    installation_steps.widget = widget
    installation_steps.remove_worthless_python_exes()
    installation_steps.extract_bundled_zip()
    installation_steps.extract_scoop_cache()

    installation_steps.install_scoop()
    installation_steps.scoop_install_git()

    installation_steps.scoop_install_pwsh()

    installation_steps.scoop_add_buckets(data["scoop"]["Buckets"])
    installation_steps.scoop_install_tooling(data["scoop"])

    installation_steps.pip_install_packages(data["pip"])

    installation_steps.npm_install_libraries(data["npm"])

    installation_steps.install_ida_plugins(data["ida_plugins"])

    installation_steps.set_file_type_associations(data["file_type_associations"])

    installation_steps.pin_apps_to_taskbar(data["taskbar_pins"])

    installation_steps.clone_git_repositories(data["git_repositories"])

    # Run IDAPySwitch to ensure that IDA Pro works immediately after installation
    installation_steps.ida_py_switch(data["ida_py_switch"])

    # Make Bindiff available to other programs
    installation_steps.make_bindiff_available_to_programs()

    # Install Zsh on top of git
    installation_steps.install_zsh_over_git()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Zsh over Git", "", InfoBarIcon.SUCCESS)

    # Install Recaf3's JavaFX dependencies to ensure it works even if VM is not connected to the internet
    installation_steps.extract_and_place_file("recaf3_javafx_dependencies.zip", utils.resolve_path(r"%APPDATA%\Recaf\dependencies"))
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Recaf3's JavaFX dependencies", "", InfoBarIcon.SUCCESS)

    # Add Npcap's annoying non-silent installer to the RunOnce registry key
    installation_steps.add_npcap_installer_to_runonce()


    # Install .NET 3.5, which is required by some older malware samples
    # installation_steps.install_net_3_5()
    # widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed .NET 3.5", "", InfoBarIcon.SUCCESS)
    # widget.rightListView.listWidget.scrollToBottom()

    installation_steps.obtain_and_place_malware_analysis_configurations()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Obtained and placed malware analysis configurations", "", InfoBarIcon.SUCCESS)

    installation_steps.enable_dark_mode()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Enabled dark mode", "", InfoBarIcon.SUCCESS)

    installation_steps.common_post_install()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Common post-installation steps", "", InfoBarIcon.SUCCESS)

    installation_steps.clean_up_disk()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Cleaned up disk", "", InfoBarIcon.SUCCESS)

    widget.progressRing.setCustomBackgroundColor(themeColor(), themeColor())
    widget.progressRing.stop()
    widget.timerWidget.stop()

    widget.completion_signal.emit()
