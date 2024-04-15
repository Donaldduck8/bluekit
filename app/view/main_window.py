# coding: utf-8
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QIcon, QDesktopServices, QColor
from PyQt5.QtWidgets import QApplication

from qfluentwidgets import (NavigationAvatarWidget, NavigationItemPosition, MessageBox, FluentWindow,
                            SplashScreen)
from qfluentwidgets import FluentIcon as FIF

from .home_interface import HomeInterface
from .scoop_interface import ScoopInterface
from .file_type_association_interface import FTAInterface
from .execution_interface import ExecutionInterface
from ..common.config import ZH_SUPPORT_URL, EN_SUPPORT_URL, cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus

# DO NOT REMOVE THIS LINE
from ..common import resource

from data import data

class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.scoopInterface = ScoopInterface(self, "Scoop Packages", data["scoop"])
        self.pipInterface = ScoopInterface(self, "PIP Packages", data["pip"])
        self.npmInterface = ScoopInterface(self, "NodeJS Packages", data["npm"])
        self.idaPluginInterface = ScoopInterface(self, "IDA Plugins", data["ida_plugins"])
        self.vsCodeExtensionInterface = ScoopInterface(self, "VSCode Extensions", data["vscode_extensions"])
        self.taskbarPinsInterface = ScoopInterface(self, "Taskbar Pins", data["taskbar_pins"])
        self.fileTypeAssociationsInterface = FTAInterface(self, "File Type Associations", data["file_type_associations"])
        self.gitRepositoryInterface = ScoopInterface(self, "Git Repositories", data["git_repositories"])
        self.executionInterface = ExecutionInterface(self, "Execution")

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)
        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        signalBus.supportSignal.connect(self.onSupport)

    def initNavigation(self):
        # add navigation items
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.scoopInterface, QIcon(':/gallery/images/icons/package.svg'), 'Scoop')
        self.addSubInterface(self.pipInterface, QIcon(':/gallery/images/icons/python.svg'), 'Python')
        self.addSubInterface(self.npmInterface, QIcon(':/gallery/images/icons/nodejs.svg'), 'NodeJS')
        self.addSubInterface(self.idaPluginInterface, FIF.TILES, 'IDA Plugins')
        self.addSubInterface(self.vsCodeExtensionInterface, QIcon(':/gallery/images/icons/code_test.svg'), 'VSCode Extensions')
        self.addSubInterface(self.taskbarPinsInterface, FIF.PIN, 'Taskbar Pins')
        self.addSubInterface(self.fileTypeAssociationsInterface, FIF.RIGHT_ARROW, 'File Type Associations')
        self.addSubInterface(self.gitRepositoryInterface, FIF.GITHUB, 'Git Repositories')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.executionInterface, FIF.PLAY, 'Execution')

        # add custom widget to bottom
        self.navigationInterface.addItem(
            routeKey='price',
            icon=Icon.PRICE,
            text="Price",
            onClick=self.onSupport,
            selectable=False,
            tooltip="Price",
            position=NavigationItemPosition.BOTTOM
        )

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/jellyfish_logo_small.png'))
        self.setWindowTitle("Irukandji")

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
