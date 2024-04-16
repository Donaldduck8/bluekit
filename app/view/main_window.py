# coding: utf-8
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (FluentWindow, NavigationItemPosition, SplashScreen)

from data import data

from .. import utils
from ..common import resource
from ..common.icon import Icon
from ..common.config import cfg
from ..common.signal_bus import signalBus
from .execution_interface import ExecutionInterface
from .file_type_association_interface import FTAInterface
from .home_interface import HomeInterface
from .scoop_interface import ScoopInterface

if not resource:
    raise ImportError("Resource not found")


class MainWindow(FluentWindow):

    def __init__(self):
        super().__init__()
        self.initWindow()

        self._executing = False

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
        self.addSubInterface(self.scoopInterface, Icon.PACKAGE, 'Scoop')
        self.addSubInterface(self.pipInterface, Icon.PYTHON, 'Python')
        self.addSubInterface(self.npmInterface, Icon.JS, 'NodeJS')
        self.addSubInterface(self.idaPluginInterface, Icon.PLUG_DISCONNECTED, 'IDA Plugins')
        self.addSubInterface(self.vsCodeExtensionInterface, Icon.CODE, 'VSCode Extensions')
        self.addSubInterface(self.taskbarPinsInterface, FIF.PIN, 'Taskbar Pins')
        self.addSubInterface(self.fileTypeAssociationsInterface, Icon.OPEN_WITH, 'File Type Associations')
        self.addSubInterface(self.gitRepositoryInterface, FIF.GITHUB, 'Git Repositories')

        # add custom widget to bottom
        self.navigationInterface.addItem(
            routeKey='price',
            icon=FIF.PLAY,
            text="Execute",
            onClick=self.onExecute,
            selectable=False,
            tooltip="Execute",
            position=NavigationItemPosition.BOTTOM
        )

        self.stackedWidget.addWidget(self.executionInterface)

        # Incredible hack to make the icons actually spaced properly !! :SMILE:
        self.navigationInterface.resize(48, self.height() + 1000)

        # add custom widget to bottom
        '''self.navigationInterface.addItem(
            routeKey='price',
            icon=Icon.PRICE,
            text="Price",
            onClick=self.onSupport,
            selectable=False,
            tooltip="Price",
            position=NavigationItemPosition.BOTTOM
        )'''

    def onExecute(self, _):
        if not self._executing:
            self._executing = True

            # Collect the data from all sub-interfaces
            scoop_data = self.scoopInterface.data
            pip_data = self.pipInterface.data
            npm_data = self.npmInterface.data
            ida_plugin_data = self.idaPluginInterface.data
            vscode_extension_data = self.vsCodeExtensionInterface.data
            taskbar_pins_data = self.taskbarPinsInterface.data
            file_type_associations_data = self.fileTypeAssociationsInterface.data
            git_repositories_data = self.gitRepositoryInterface.data

            execution_data = {
                'scoop': scoop_data,
                'pip': pip_data,
                'npm': npm_data,
                'ida_plugins': ida_plugin_data,
                'vscode_extensions': vscode_extension_data,
                'taskbar_pins': taskbar_pins_data,
                'file_type_associations': file_type_associations_data,
                'git_repositories': git_repositories_data,
                "ida_py_switch": utils.resolve_path("%USERPROFILE%\\scoop\\apps\\python311\\current\\python311.dll"),
            }

            self.executionInterface.execute(
                execution_data
            )

        # Open the executionInterface
        self.stackedWidget.setCurrentWidget(self.executionInterface, popOut=False)

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

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())

    def onSupport(self, _):
        pass