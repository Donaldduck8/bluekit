# coding: utf-8
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QDesktopServices, QColor
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen)
from qfluentwidgets import FluentIcon as FIF

from .gallery_interface import GalleryInterface
from .home_interface import HomeInterface
from .scoop_interface import ScoopInterface
from .file_type_association_interface import FTAInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from ..common.translator import Translator

# DO NOT REMOVE THIS LINE
from ..common import resource

from data import data

class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.scoopInterface = ScoopInterface(self, data["scoop"])
        self.pipInterface = ScoopInterface(self, data["pip"])
        self.npmInterface = ScoopInterface(self, data["npm"])
        self.idaPluginInterface = ScoopInterface(self, data["ida_plugins"])
        self.vsCodeExtensionInterface = ScoopInterface(self, data["vscode_extensions"])
        self.taskbarPinsInterface = ScoopInterface(self, data["taskbar_pins"])
        self.fileTypeAssociationsInterface = FTAInterface(self, data["file_type_associations"])
        self.gitRepositoryInterface = ScoopInterface(self, data["git_repositories"])

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)
        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.switchToSampleCard.connect(self.switchToSample)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        t = Translator()
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('Home'))
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.scoopInterface, FIF.DEVELOPER_TOOLS, self.tr('Scoop'))
        self.addSubInterface(self.pipInterface, FIF.IOT, self.tr('Python'))
        self.addSubInterface(self.npmInterface, FIF.LEAF, self.tr('NodeJS'))
        self.addSubInterface(self.idaPluginInterface, FIF.TILES, self.tr('IDA Plugins'))
        self.addSubInterface(self.vsCodeExtensionInterface, FIF.ROBOT, self.tr('VSCode Extensions'))
        self.addSubInterface(self.taskbarPinsInterface, FIF.PIN, self.tr('Taskbar Pins'))
        self.addSubInterface(self.fileTypeAssociationsInterface, FIF.RIGHT_ARROW, self.tr('File Type Associations'))
        self.addSubInterface(self.gitRepositoryInterface, FIF.GITHUB, self.tr('Git Repositories'))

        # add custom widget to bottom
        self.navigationInterface.addItem(
            routeKey='price',
            icon=Icon.PRICE,
            text=t.price,
            onClick=self.onSupport,
            selectable=False,
            tooltip=t.price,
            position=NavigationItemPosition.BOTTOM
        )

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/logo.png'))
        self.setWindowTitle("Setup")

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # create splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

    def onSupport(self):
        language = cfg.get(cfg.language).value
        if language.name() == "zh_CN":
            QDesktopServices.openUrl(QUrl(ZH_SUPPORT_URL))
        else:
            QDesktopServices.openUrl(QUrl(EN_SUPPORT_URL))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def switchToSample(self, routeKey, index):
        """ switch to sample """
        interfaces = self.findChildren(GalleryInterface)
        for w in interfaces:
            if w.objectName() == routeKey:
                self.stackedWidget.setCurrentWidget(w, False)
                w.scrollToCard(index)
