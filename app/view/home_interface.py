# coding:utf-8
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from qfluentwidgets import ScrollArea, FluentIcon
from ..common.config import HELP_URL, REPO_URL, BLOG_URL, FEEDBACK_URL
from ..components.link_card import LinkCardView
from ..common.style_sheet import StyleSheet


class BannerWidget(QWidget):
    """ Banner widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # self.setFixedHeight(336)

        self.vBoxLayout = QVBoxLayout(self)

        # Make sure this label is white
        # self.galleryLabel = QLabel('Malware Analysis VM', self)
        # self.galleryLabel.setStyleSheet('color: black; font-size: 55px; font-weight: light; text-align: center;')

        self.banner = QPixmap(':/gallery/images/splash.png')
        self.linkCardView = LinkCardView(self)

        # self.galleryLabel.setObjectName('galleryLabel')

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 32, 20)
        # self.vBoxLayout.addWidget(self.galleryLabel, 1, Qt.AlignCenter | Qt.AlignTop)
        self.vBoxLayout.addWidget(self.linkCardView, 1, Qt.AlignBottom)
        self.vBoxLayout.setAlignment(Qt.AlignCenter)

        self.linkCardView.addCard(
            ':/gallery/images/logo.png',
            self.tr('Getting started'),
            self.tr('An overview of app development options and samples.'),
            HELP_URL
        )

        self.linkCardView.addCard(
            FluentIcon.GITHUB,
            self.tr('Scoop Bucket'),
            self.tr(
                'Contribute applications to the Malware Analysis Scoop bucket.'),
            REPO_URL
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
            self.tr('Help us improve PyQt-Fluent-Widgets by providing feedback.'),
            FEEDBACK_URL
        )

    def paintEvent(self, e):
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        # Scale the pixmap to a specific width while keeping the aspect ratio
        pixmap = self.banner.scaledToWidth(self.width() * 0.82, Qt.SmoothTransformation)

        # Calculate the top-left position to center the pixmap in the widget
        x = (self.width() - pixmap.width()) / 2
        y = (self.height() - pixmap.height()) / 3

        # Define the rounded rectangle path
        path = QPainterPath()
        path.addRoundedRect(QRectF(x, y, pixmap.width(), pixmap.height()), 13, 13)  # 13 is the radius for corners

        # Set the clipping path with rounded corners
        painter.setClipPath(path)

        # Draw the pixmap at the calculated position within the clipped region
        painter.drawPixmap(x, y, pixmap)


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