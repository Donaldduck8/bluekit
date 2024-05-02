# coding: utf-8
import os
import zipfile

from argparse import Namespace

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (FluentWindow, MessageBox, NavigationItemPosition,
                            SplashScreen)

from app import data

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

    def validateBundledApplications(self, bluekit_configuration: data.Configuration):
        potentially_bundled_packages: list[data.ScoopPackage] = []
        for _category, packages in bluekit_configuration.scoop.packages.items():
            packages: list[data.ScoopPackage]

            potentially_bundled_packages += [package for package in packages if package.id.endswith(".json")]

        actually_bundled_manifests = []
        actually_bundled_zips = []

        if cfg.bundledZipFile.value and os.path.isfile(cfg.bundledZipFile.value) and zipfile.is_zipfile(cfg.bundledZipFile.value):
            with zipfile.ZipFile(cfg.bundledZipFile.value, 'r') as zip_ref:
                actually_bundled_manifests = [name for name in zip_ref.namelist() if name.endswith(".json")]
                actually_bundled_zips = [name for name in zip_ref.namelist() if name.endswith(".zip")]

        not_bundled_packages = [package for package in potentially_bundled_packages if package.id not in actually_bundled_manifests or package.id.replace(".json", ".zip") not in actually_bundled_zips]

        if len(not_bundled_packages) == 0:
            return True

        not_bundled_messages = []

        for package in not_bundled_packages:
            if package.alternative is not None:
                not_bundled_messages.append(f"{package.name} ({package.id}) - Installing {package.alternative.name}")
            else:
                not_bundled_messages.append(f"{package.name} ({package.id}) - No alternative specified")

        not_bundled_message = '\n'.join(not_bundled_messages)

        # Show an information pop-up
        title = 'Bundled Applications'

        content = f"""The following bundled applications are not present in the provided .zip file:

{not_bundled_message}

Would you like to proceed anyway?"""
        w = MessageBox(title, content, self)
        w.show()

        if not w.exec():
            w.close()
            return False

        w.close()
        return True


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

            bluekit_configuration = data.Configuration.empty()
            bluekit_configuration.scoop = self.scoopInterface.data
            bluekit_configuration.pip = self.pipInterface.data
            bluekit_configuration.npm = self.npmInterface.data
            bluekit_configuration.ida_plugins = self.idaPluginInterface.data
            bluekit_configuration.vscode_extensions = self.vsCodeExtensionInterface.data
            bluekit_configuration.taskbar_pins = self.taskbarPinsInterface.data
            bluekit_configuration.file_type_associations = self.fileTypeAssociationsInterface.data
            bluekit_configuration.git_repositories = self.gitRepositoryInterface.data
            bluekit_configuration.registry_changes = self.registryChangesInterface.data
            bluekit_configuration.misc_files = self.miscFilesInterface.data
            bluekit_configuration.settings = data.BluekitSettings(**execution_settings)

            if not self.validateBundledApplications(bluekit_configuration):
                return

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
                bluekit_configuration
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
