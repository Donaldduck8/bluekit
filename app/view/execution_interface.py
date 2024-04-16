# coding:utf-8
import logging
import threading
from enum import Enum
from typing import Union

from PyQt5.QtCore import (QEvent, QPropertyAnimation, QRectF, QSize, Qt,
                          pyqtSignal, QTime, QTimer, QRect)
from PyQt5.QtGui import QColor, QIcon, QPainter, QResizeEvent
from PyQt5.QtWidgets import (QFrame, QGraphicsOpacityEffect, QHBoxLayout,
                             QLabel, QListWidgetItem, QVBoxLayout, QWidget, QStackedWidget, QSizePolicy)
from qfluentwidgets import (FluentIconBase, FluentStyleSheet,
                            IndeterminateProgressRing, InfoBarIcon,
                            InfoBarPosition, ListWidget, TitleLabel)
from qfluentwidgets.common.auto_wrap import TextWrap
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.common.icon import Theme, drawIcon, isDarkTheme
from qfluentwidgets.common.style_sheet import FluentStyleSheet, themeColor
from qfluentwidgets.components.widgets.button import TransparentToolButton
from qfluentwidgets.components.widgets.list_view import ListWidget
from qfluentwidgets import SubtitleLabel

from .. import installation_steps, utils
from ..common.style_sheet import StyleSheet


class ListWidgetLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.bottomListView.listWidget.addItem(msg)
        self.widget.bottomListView.listWidget.scrollToBottom()


class Frame(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(4, 8, 4, 8)

        self.setObjectName('frame')
        StyleSheet.VIEW_INTERFACE.apply(self)

    def addWidget(self, widget):
        self.hBoxLayout.addWidget(widget)


class ListFrame(Frame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.listWidget = CustomListWidget(self)
        self.addWidget(self.listWidget)


class InfoBarIcon(FluentIconBase, Enum):
    """ Info bar icon """

    INFORMATION = "Info"
    SUCCESS = "Success"
    WARNING = "Warning"
    ERROR = "Error"

    def path(self, theme=Theme.AUTO):
        if theme == Theme.AUTO:
            color = "dark" if isDarkTheme() else "light"
        else:
            color = theme.value.lower()

        return f':/qfluentwidgets/images/info_bar/{self.value}_{color}.svg'


class InfoBarPosition(Enum):
    """ Info bar position """
    TOP = 0
    BOTTOM = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5
    NONE = 6


class InfoIconWidget(QWidget):
    """ Icon widget """

    def __init__(self, icon: InfoBarIcon, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(36, 36)
        self.icon = icon

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        rect = QRectF(10, 10, 15, 15)
        if self.icon != InfoBarIcon.INFORMATION:
            drawIcon(self.icon, painter, rect)
        else:
            drawIcon(self.icon, painter, rect, indexes=[0], fill=themeColor().name())


class InfoBar(QFrame):
    """ Information bar """

    closedSignal = pyqtSignal()

    def __init__(self, icon: Union[InfoBarIcon, FluentIconBase, QIcon, str], title: str, content: str,
                 orient=Qt.Horizontal, isClosable=True, duration=1000, position=InfoBarPosition.TOP_RIGHT,
                 parent=None):
        """
        Parameters
        ----------
        icon: InfoBarIcon | FluentIconBase | QIcon | str
            the icon of info bar

        title: str
            the title of info bar

        content: str
            the content of info bar

        orient: Qt.Orientation
            the layout direction of info bar, use `Qt.Horizontal` for short content

        isClosable: bool
            whether to show the close button

        duraction: int
            the time for info bar to display in milliseconds. If duration is less than zero,
            info bar will never disappear.

        parent: QWidget
            parent widget
        """
        super().__init__(parent=parent)
        self.title = title
        self.content = content
        self.orient = orient
        self.icon = icon
        self.duration = duration
        self.isClosable = isClosable
        self.position = position

        self.titleLabel = QLabel(self)
        self.contentLabel = QLabel(self)
        self.closeButton = TransparentToolButton(FIF.CLOSE, self)
        self.iconWidget = InfoIconWidget(icon)

        self.hBoxLayout = QHBoxLayout(self)
        self.textLayout = QHBoxLayout() if self.orient == Qt.Horizontal else QVBoxLayout()
        self.widgetLayout = QHBoxLayout() if self.orient == Qt.Horizontal else QVBoxLayout()

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(
            self.opacityEffect, b'opacity', self)

        self.lightBackgroundColor = None
        self.darkBackgroundColor = None

        self.__initWidget()

    def __initWidget(self):
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)

        self.closeButton.setFixedSize(36, 36)
        self.closeButton.setIconSize(QSize(12, 12))
        self.closeButton.setCursor(Qt.PointingHandCursor)
        self.closeButton.setVisible(self.isClosable)

        self.__setQss()
        self.__initLayout()

        self.closeButton.clicked.connect(self.close)

    def __initLayout(self):
        # self.hBoxLayout.setContentsMargins(6, 6, 6, 6)
        self.hBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.textLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.textLayout.setAlignment(Qt.AlignTop)
        self.textLayout.setContentsMargins(0, 8, 0, 8)

        self.hBoxLayout.setSpacing(0)
        # self.textLayout.setSpacing(5)

        # add icon to layout
        self.hBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignTop | Qt.AlignLeft)

        # add title to layout
        self.textLayout.addWidget(self.titleLabel, 1, Qt.AlignTop)
        self.titleLabel.setVisible(bool(self.title))

        # add content label to layout
        # if self.orient == Qt.Horizontal:
        #     self.textLayout.addSpacing(7)

        self.textLayout.addWidget(self.contentLabel, 1, Qt.AlignLeft | Qt.AlignTop)
        self.contentLabel.setVisible(bool(self.content))
        self.hBoxLayout.addLayout(self.textLayout, stretch=1)

        # add widget layout
        if self.orient == Qt.Horizontal:
            self.hBoxLayout.addLayout(self.widgetLayout)
            self.widgetLayout.setSpacing(10)
        else:
            self.textLayout.addLayout(self.widgetLayout)

        # add close button to layout
        if self.isClosable:
            self.hBoxLayout.addSpacing(4)
            self.hBoxLayout.addWidget(self.closeButton, 0, Qt.AlignTop | Qt.AlignLeft)

        self._adjustText()

    def __setQss(self):
        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')
        if isinstance(self.icon, Enum):
            self.setProperty('type', self.icon.value)

        FluentStyleSheet.INFO_BAR.apply(self)

    def __fadeOut(self):
        """ fade out """
        self.opacityAni.setDuration(200)
        self.opacityAni.setStartValue(1)
        self.opacityAni.setEndValue(0)
        self.opacityAni.finished.connect(self.close)
        self.opacityAni.start()

    def _adjustText(self):
        w = 900 if not self.parent() else (self.parent().width() - 50)

        # adjust title
        # chars = max(min(w / 10, 120), 30)
        self.titleLabel.setText(TextWrap.wrap(self.title, 50, False)[0])

        # adjust content
        # chars = max(min(w / 9, 120), 30)
        # self.contentLabel.setText(TextWrap.wrap(self.content, chars, False)[0])
        self.adjustSize()

    def addWidget(self, widget: QWidget, stretch=0):
        """ add widget to info bar """
        self.widgetLayout.addSpacing(6)
        align = Qt.AlignTop if self.orient == Qt.Vertical else Qt.AlignVCenter
        self.widgetLayout.addWidget(widget, stretch, Qt.AlignLeft | align)

    def setCustomBackgroundColor(self, light, dark):
        """ set the custom background color

        Parameters
        ----------
        light, dark: str | Qt.GlobalColor | QColor
            background color in light/dark theme mode
        """
        self.lightBackgroundColor = QColor(light)
        self.darkBackgroundColor = QColor(dark)
        self.update()

    def eventFilter(self, obj, e: QEvent):
        if obj is self.parent():
            if e.type() in [QEvent.Resize, QEvent.WindowStateChange]:
                self._adjustText()

        return super().eventFilter(obj, e)

    def closeEvent(self, e):
        self.closedSignal.emit()
        self.deleteLater()

    def showEvent(self, e):
        self._adjustText()
        super().showEvent(e)

        if self.parent():
            self.parent().installEventFilter(self)

    def paintEvent(self, e):
        super().paintEvent(e)
        
        if self.lightBackgroundColor is None:
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if isDarkTheme():
            painter.setBrush(self.darkBackgroundColor)
        else:
            painter.setBrush(self.lightBackgroundColor)

        rect = self.rect().adjusted(1, 1, -1, -1)
        painter.drawRoundedRect(rect, 6, 6)

    def resizeEvent(self, a0) -> None:
        super().resizeEvent(a0)
        FluentStyleSheet.INFO_BAR.apply(self)


class CustomListWidget(ListWidget):
    add_infobar_signal = pyqtSignal(str, str, str)  # Signal to update the list widget safely

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWordWrap(True)
        self.add_infobar_signal.connect(self.add_infobar)

        FluentStyleSheet.LIST_VIEW.apply(self)

        self.setContentsMargins(0, 400, 8, 4)
        self.setViewportMargins(0, 4, 0, 4)

    def add_infobar(self, title, content):
        item = QListWidgetItem()

        infoBar = InfoBar(
            icon=InfoBarIcon.SUCCESS,
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


class Timer(QWidget):
    def __init__(self):
        super().__init__()

        self.startTime = QTime(0, 0, 0)

        self.initUI()
        
    def initUI(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        
        self.label = QLabel("00:00:00", self)
        self.label.setAlignment(Qt.AlignCenter)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        
        self.timer.start(1000)  # Timer updates every second
        
    def showTime(self):
        self.startTime = self.startTime.addSecs(1)
        self.label.setText(self.startTime.toString("hh:mm:ss"))


class FluentTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
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
        print("Executing")

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


def threading_function_test(widget: ExecutionInterface, data: dict):
    for i in range(5):
        import random

        # widget.rightListView.listWidget.addItem("Item " + str(i))
        widget.rightListView.listWidget.add_infobar_signal.emit("Success: " + "word " * int(random.random() * 21), "", "")

        # Add a standard list item to the bottom list view
        widget.bottomListView.listWidget.addItem(QListWidgetItem("Item " + str(i)))
        widget.bottomListView.listWidget.scrollToBottom()
        widget.rightListView.listWidget.scrollToBottom()
        import time
        time.sleep(1)

    widget.progressRing.setCustomBackgroundColor(themeColor(), themeColor())
    widget.progressRing.stop()
    widget.timerWidget.stop()


def threading_function(widget: ExecutionInterface, data: dict):
    installation_steps.remove_worthless_python_exes()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Removed AppAlias Python executables", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.extract_bundled_zip()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Extracted bundled .zip file, if present", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.extract_scoop_cache()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Extracted Scoop cache", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.install_scoop()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Scoop", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.scoop_install_git()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Git", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.scoop_install_pwsh()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed PowerShell", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.scoop_add_buckets(data["scoop"]["Buckets"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Added Scoop buckets", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.scoop_install_tooling(data["scoop"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Scoop tooling", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.pip_install_packages(data["pip"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed pip packages", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.npm_install_libraries(data["npm"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed npm libraries", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.install_ida_plugins(data["ida_plugins"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed IDA Pro plugins", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.set_file_type_associations(data["file_type_associations"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Set file type associations", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.pin_apps_to_taskbar(data["taskbar_pins"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Pinned apps to taskbar", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.clone_git_repositories(data["git_repositories"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Cloned Git repositories", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    # Run IDAPySwitch to ensure that IDA Pro works immediately after installation
    installation_steps.ida_py_switch(data["ida_py_switch"])
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Ran IDAPySwitch", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    # Make Bindiff available to other programs
    installation_steps.make_bindiff_available_to_programs()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Made BinDiff available to other programs", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    # Install Zsh on top of git
    installation_steps.install_zsh_over_git()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Zsh over Git", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    # Install Recaf3's JavaFX dependencies to ensure it works even if VM is not connected to the internet
    installation_steps.extract_and_place_file("recaf3_javafx_dependencies.zip", utils.resolve_path(r"%APPDATA%\Recaf\dependencies"))
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed Recaf3's JavaFX dependencies", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    # Add Npcap's annoying non-silent installer to the RunOnce registry key
    installation_steps.add_npcap_installer_to_runonce()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Added Npcap installer to RunOnce", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    # Install .NET 3.5, which is required by some older malware samples
    # installation_steps.install_net_3_5()
    # widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed .NET 3.5", "", "")
    # widget.rightListView.listWidget.scrollToBottom()

    installation_steps.obtain_and_place_malware_analysis_configurations()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Obtained and placed malware analysis configurations", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.enable_dark_mode()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Enabled dark mode", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.common_post_install()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Common post-installation steps", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    installation_steps.clean_up_disk()
    widget.rightListView.listWidget.add_infobar_signal.emit("Success: Cleaned up disk", "", "")
    widget.rightListView.listWidget.scrollToBottom()

    widget.progressRing.setCustomBackgroundColor(themeColor(), themeColor())
    widget.progressRing.stop()
    widget.timerWidget.stop()

    # installation_steps.restart()