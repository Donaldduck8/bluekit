# coding: utf-8
from argparse import Namespace

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (FluentWindow, MessageBox, NavigationItemPosition,
                            SplashScreen)

import app.data as data

from .. import utils
from ..common import resource
from ..common.config import cfg
from ..common.icon import Icon
from ..common.signal_bus import signalBus
from .execution_interface import ExecutionInterface
from .file_type_association_interface import FileTypeAssocWidget
from .home_interface import HomeInterface
from .miscellaneous_files_interface import MiscFilesTreeWidget
from .package_tree_interface import PackageTreeWidget
from .registry_changes_interface import RegistryChangesWidget
from .settings_interface import SettingsInterface

if not resource:
    raise ImportError("Resource not found")


class MainWindow(FluentWindow):

    def __init__(self, args: Namespace = None):
        super().__init__()
        self.initWindow()

        self._executing = False

        self.args = args

        # create sub interface
        self.homeInterface = HomeInterface(self)
        self.scoopInterface = PackageTreeWidget(self, "Scoop Packages", data.configuration.scoop)
        self.pipInterface = PackageTreeWidget(self, "PIP Packages", data.configuration.pip)
        self.npmInterface = PackageTreeWidget(self, "NodeJS Packages", data.configuration.npm)
        self.idaPluginInterface = PackageTreeWidget(self, "IDA Plugins", data.configuration.ida_plugins)
        self.vsCodeExtensionInterface = PackageTreeWidget(self, "VSCode Extensions", data.configuration.vscode_extensions)
        self.taskbarPinsInterface = PackageTreeWidget(self, "Taskbar Pins", data.configuration.taskbar_pins)
        self.fileTypeAssociationsInterface = FileTypeAssocWidget(self, "File Type Associations", data.configuration.file_type_associations)
        self.gitRepositoryInterface = PackageTreeWidget(self, "Git Repositories", data.configuration.git_repositories)
        self.registryChangesInterface = RegistryChangesWidget(self, "Registry", data.configuration.registry_changes)
        self.miscFilesInterface = MiscFilesTreeWidget(self, "Miscellaneous Files", data.configuration.misc_files)
        self.executionInterface = ExecutionInterface(self)

        self.settingsInterface = SettingsInterface(self)

        # enable acrylic effect
        self.navigationInterface.setAcrylicEnabled(True)
        self.setCustomBackgroundColor(QColor(240, 244, 249), QColor(32, 32, 32))

        self.connectSignalToSlot()

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def connectSignalToSlot(self):
        signalBus.micaEnableChanged.connect(self.setMicaEffectEnabled)

    def initNavigation(self):
        # add navigation items
        self.addSubInterface(self.homeInterface, FIF.HOME, 'Home')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.scoopInterface, Icon.PACKAGE, 'Scoop')
        self.addSubInterface(self.pipInterface, Icon.PYTHON, 'Python')
        self.addSubInterface(self.npmInterface, Icon.JS, 'NodeJS')
        self.addSubInterface(self.idaPluginInterface, Icon.PLUG_DISCONNECTED, 'IDA Plugins')
        self.addSubInterface(self.vsCodeExtensionInterface, Icon.CODE, 'VSCode Extensions')
        self.addSubInterface(self.fileTypeAssociationsInterface, Icon.OPEN_WITH, 'File Type Associations')
        self.addSubInterface(self.gitRepositoryInterface, FIF.GITHUB, 'Git Repositories')
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.taskbarPinsInterface, FIF.PIN, 'Taskbar Pins')
        self.addSubInterface(self.registryChangesInterface, Icon.REGISTRY_EDITOR, 'Registry Changes')
        self.addSubInterface(self.miscFilesInterface, FIF.FOLDER, 'Miscellaneous Files')

        self.addSubInterface(
            self.settingsInterface, FIF.SETTING, "Settings", NavigationItemPosition.BOTTOM)

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

    def onExecute(self, _):
        if not self._executing:
            interfaces = [
                self.scoopInterface,
                self.pipInterface,
                self.npmInterface,
                self.idaPluginInterface,
                self.vsCodeExtensionInterface,
                self.taskbarPinsInterface,
                self.fileTypeAssociationsInterface,
                self.gitRepositoryInterface,
                self.registryChangesInterface,
                self.miscFilesInterface
            ]

            execution_settings = {
                'enable_windows_safer': cfg.saferEnabled.value,
                'malware_folders': [utils.resolve_path(x) for x in cfg.malwareFolders.value],
                'install_zsh_over_git': cfg.installZsh.value,
                'make_bindiff_available': cfg.makeBindiffAvailable.value,
                "ida_py_switch": utils.resolve_path("%USERPROFILE%\\scoop\\apps\\python311\\current\\python311.dll"),
            }

            execution_data = data.Configuration.empty()
            execution_data.scoop = self.scoopInterface.data
            execution_data.pip = self.pipInterface.data
            execution_data.npm = self.npmInterface.data
            execution_data.ida_plugins = self.idaPluginInterface.data
            execution_data.vscode_extensions = self.vsCodeExtensionInterface.data
            execution_data.taskbar_pins = self.taskbarPinsInterface.data
            execution_data.file_type_associations = self.fileTypeAssociationsInterface.data
            execution_data.git_repositories = self.gitRepositoryInterface.data
            execution_data.registry_changes = self.registryChangesInterface.data
            execution_data.misc_files = self.miscFilesInterface.data
            execution_data.settings = data.BluekitSettings(**execution_settings)

            # Show a confirmation pop-up
            title = 'Start the installation?'
            content = """The installation process may take upward of 60 minutes to complete. Would you like to proceed?"""
            w = MessageBox(title, content, self)
            w.show()

            if not w.exec():
                w.close()
                return

            w.close()

            self._executing = True

            # Disable all settings
            self.settingsInterface.on_execution_started()

            # Make all widgets non-editable
            for interface in interfaces:
                interface.on_execution_started()

            self.executionInterface.execute(
                execution_data
            )

        # Open the executionInterface
        self.stackedWidget.setCurrentWidget(self.executionInterface, popOut=False)

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon(':/gallery/images/jellyfish_logo_small.png'))
        self.setWindowTitle(f"Bluekit {data.VERSION}")

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        # Create a temporary splash screen
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(106, 106))
        self.splashScreen.raise_()

        # Open the window in the center of the screen
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, 'splashScreen'):
            self.splashScreen.resize(self.size())
