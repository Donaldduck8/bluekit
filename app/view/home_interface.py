# coding:utf-8
# pylint: disable=E1101
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QPainterPath, QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, ScrollArea

from ..common.config import BLOG_URL, BUCKET_URL, FEEDBACK_URL, HELP_URL
from ..common.style_sheet import StyleSheet
from ..components.link_card import LinkCardView


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.vBoxLayout = QVBoxLayout(self)
        self.banner = QPixmap(':/gallery/images/splash.png')
        self.linkCardView = LinkCardView(self)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 32, 20)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

        self.linkCardView.addCard(
            ':/gallery/images/jellyfish_logo_small.png',
            self.tr('Bluekit'),
            self.tr('An all-in-one setup script for cybersecurity workstations.'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('Scoop Bucket'),
            self.tr(
                'Contribute applications to the Malware Analysis Scoop bucket.'),
            BUCKET_URL
        )

        self.linkCardView.addCard(
            ':/gallery/images/avatar.png',
            self.tr('Author\'s Blog'),
            self.tr(
                'Check out the author\'s blog for malware analysis and technical escapades.'),
            BLOG_URL
        )

        self.linkCardView.addCard(
            FluentIcon.FEEDBACK,
            self.tr('Send feedback'),
            self.tr('Help us improve Bluekit by providing feedback.'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # Scale the pixmap to a specific width while keeping the aspect ratio
        pixmap = self.banner.scaledToWidth(int(self.width() * 0.82), Qt.SmoothTransformation)

        # Calculate the top-left position to center the pixmap in the widget
        x = (self.width() - pixmap.width()) / 2
        y = (self.height() - pixmap.height()) / 3

        # Define the rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, pixmap.width(), pixmap.height()), 13, 13)  # 13 is the radius for corners

        # Set the clipping path with rounded corners
        painter.setClipPath(path)

        # Draw the pixmap at the calculated position within the clipped region
        painter.drawPixmap(int(x), int(y), pixmap)
        painter.end()


class HomeInterface(ScrollArea):
    """ Home interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.banner = BannerWidget(self)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.__initWidget()

    def __initWidget(self):
        self.view.setObjectName('view')
        self.setObjectName('homeInterface')
        StyleSheet.HOME_INTERFACE.apply(self)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.addWidget(self.banner)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
