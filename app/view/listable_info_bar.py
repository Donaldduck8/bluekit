# coding:utf-8
import time
from enum import Enum
from typing import Union

from PyQt5.QtCore import QEvent, QPropertyAnimation, QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFontMetrics, QIcon, QPainter
from PyQt5.QtWidgets import (QFrame, QGraphicsOpacityEffect, QHBoxLayout,
                             QLabel, QSizePolicy, QVBoxLayout, QWidget)
from qfluentwidgets import FluentIconBase, InfoBarIcon, InfoBarPosition
from qfluentwidgets.common.auto_wrap import TextWrap
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.common.icon import drawIcon, isDarkTheme
from qfluentwidgets.common.style_sheet import FluentStyleSheet, themeColor
from qfluentwidgets.components.widgets.button import TransparentToolButton


class InfoIconWidget(QWidget):
    """ Icon widget """

    def __init__(self, icon: InfoBarIcon, parent=None):
        super().__init__(parent=parent)
        self.setFixedSize(18, 18)
        self.icon = icon

    def paintEvent(self, _e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        rect = QRectF(2, 2, 15, 15)
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
        self.timestampLabel = QLabel(self)
        self.timestampLabel.setObjectName('timestampLabel')

        self.hBoxLayout = QHBoxLayout(self)
        self.textLayout = QHBoxLayout() if self.orient == Qt.Horizontal else QVBoxLayout()
        self.widgetLayout = QHBoxLayout() if self.orient == Qt.Horizontal else QVBoxLayout()

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.opacityAni = QPropertyAnimation(
            self.opacityEffect, b'opacity', self)

        self.lightBackgroundColor = None
        self.darkBackgroundColor = None

        # LOL WTF
        self.setMaximumWidth(self.parent().width() - 500)

        self.__initWidget()

    def __initWidget(self):
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)

        self.closeButton.setCursor(Qt.PointingHandCursor)
        self.closeButton.setVisible(self.isClosable)

        self.__setQss()
        self.__initLayout()

        self.closeButton.clicked.connect(self.close)

    def __initLayout(self):
        self.hBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.textLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.textLayout.setAlignment(Qt.AlignTop)

        self.hBoxLayout.setSpacing(0)
        # self.textLayout.setSpacing(5)

        # add icon to layout
        self.hBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignTop | Qt.AlignLeft)
        self.hBoxLayout.addSpacing(6)

        # add title to layout
        self.textLayout.addWidget(self.titleLabel, 1, Qt.AlignTop | Qt.AlignLeft)
        self.titleLabel.setVisible(bool(self.title))

        timestampText = time.strftime('%H:%M:%S', time.localtime())
        self.timestampLabel.setText(timestampText)
        self.textLayout.addWidget(self.timestampLabel, 0, Qt.AlignRight)

        # Set textLayout to resize itself or whatever
        self.textLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.titleLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

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

    def _adjustText(self):

        def calculate_average_char_width(font):
            # Create a QFontMetrics object for the given font
            metrics = QFontMetrics(font)
            # Get the average width of characters using QFontMetrics
            average_width = metrics.averageCharWidth()
            return average_width

        parent = self.parent()

        if parent:
            w = parent.width() - 50
        else:
            w = 900

        numChars = int(w / calculate_average_char_width(self.titleLabel.font()))

        # Convert from pixel width to character width
        self.titleLabel.setText(TextWrap.wrap(self.title, numChars * 0.9, False)[0])

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

    def closeEvent(self, _e):
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
