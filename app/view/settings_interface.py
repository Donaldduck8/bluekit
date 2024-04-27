# coding:utf-8
import types

from PyQt5.QtCore import QStandardPaths, Qt
from PyQt5.QtWidgets import QLabel, QWidget, QFileDialog
from qfluentwidgets import ExpandLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (FolderListSettingCard, InfoBar, ScrollArea,
                            SettingCardGroup, SwitchSettingCard, qconfig, PrimaryPushSettingCard)

from ..common.config import cfg
from ..common.style_sheet import StyleSheet


# Globally disable configuration saving, because qfluentwidgets randomly calls this function and writes a file to disk
def save(_self):
    pass


qconfig.save = types.MethodType(save, qconfig)


class SettingsInterface(ScrollArea):
    """ Setting interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = QLabel("Settings", self)

        self.bundledFileGroup = SettingCardGroup(
            "Bundled Files", self.scrollWidget
        )
        self.bundledFileCard = PrimaryPushSettingCard(
            self.tr('Choose bundled .zip file'),
            FIF.DOWNLOAD,
            self.tr("Bundled .zip file"),
            cfg.get(cfg.bundledZipFile),
            self.bundledFileGroup
        )

        self.installBuildToolsGroup = SettingCardGroup(
            "Visual C++ Build Tools", self.scrollWidget
        )
        self.installBuildToolsCard = SwitchSettingCard(
            FIF.LIBRARY,
            "Install Visual C++ Build Tools",
            "Allows for the installation of Rust, netifaces and other packages that require the Visual C++ Build Tools.",
            cfg.installBuildTools,
            self.installBuildToolsGroup
        )

        # Groups
        self.malwareSafetyGroup = SettingCardGroup(
            "Malware Safety", self.scrollWidget)
        self.saferCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            'Enable the Windows Safer feature',
            'Prevents program and script execution within specified folders. Make sure to disable this setting for a dynamic analysis environment!',
            cfg.saferEnabled,
            self.malwareSafetyGroup
        )

        self.malwareFolderCard = FolderListSettingCard(
            cfg.malwareFolders,
            "Folders with execution disabled",
            content="Add folders to prevent execution of files within them.",
            directory=QStandardPaths.writableLocation(QStandardPaths.HomeLocation),
            parent=self.malwareSafetyGroup
        )
        self.malwareFolderCard.setValue(cfg.malwareFolders.value)

        self.scoopGroup = SettingCardGroup(
            "Scoop", self.scrollWidget)
        self.keepCacheCard = SwitchSettingCard(
            FIF.SAVE,
            'Keep Scoop cache',
            'Keep downloaded files after installing a package. Useful if performing multiple installs.',
            cfg.scoopKeepCache,
            self.scoopGroup
        )

        self.bindiffGroup = SettingCardGroup(
            "BinDiff", self.scrollWidget)
        self.makeBindiffAvailableCard = SwitchSettingCard(
            FIF.APPLICATION,
            'Make BinDiff available',
            'Create additional plug-ins to make BinDiff available to IDA Pro and Binary Ninja, if possible.',
            cfg.makeBindiffAvailable,
            self.bindiffGroup
        )

        self.zshGroup = SettingCardGroup(
            "Zsh", self.scrollWidget)
        self.installZshCard = SwitchSettingCard(
            FIF.APPLICATION,
            'Install Zsh on top of Git using Symlinks',
            'Enables the use of Zsh in Git Bash, and allows for the use of Oh My Zsh. (Required if using default configuration)',
            cfg.installZsh,
            self.zshGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # initialize style sheet
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)  # pylint: disable=no-member

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        # add cards to group
        self.bundledFileGroup.addSettingCard(self.bundledFileCard)

        self.installBuildToolsGroup.addSettingCard(self.installBuildToolsCard)

        self.malwareSafetyGroup.addSettingCard(self.saferCard)
        self.malwareSafetyGroup.addSettingCard(self.malwareFolderCard)

        self.scoopGroup.addSettingCard(self.keepCacheCard)

        self.bindiffGroup.addSettingCard(self.makeBindiffAvailableCard)

        self.zshGroup.addSettingCard(self.installZshCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.bundledFileGroup)
        self.expandLayout.addWidget(self.installBuildToolsGroup)
        self.expandLayout.addWidget(self.malwareSafetyGroup)
        self.expandLayout.addWidget(self.scoopGroup)
        self.expandLayout.addWidget(self.bindiffGroup)
        self.expandLayout.addWidget(self.zshGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            'Updated successfully',
            'Configuration takes effect after restart',
            duration=1500,
            parent=self
        )

    def __onBundledZipFileClicked(self):
        bundled_file_path_result = QFileDialog.getOpenFileName(self, self.tr("Choose bundled file"), "./", "Zip files (*.zip)")

        if not bundled_file_path_result or not bundled_file_path_result[0]:
            return

        bundled_file_path = bundled_file_path_result[0]

        if cfg.get(cfg.bundledZipFile) == bundled_file_path:
            return

        cfg.set(cfg.bundledZipFile, bundled_file_path)
        self.bundledFileCard.setContent(bundled_file_path)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)

        self.saferCard.checkedChanged.connect(self.malwareFolderCard.setEnabled)
        self.bundledFileCard.clicked.connect(self.__onBundledZipFileClicked)

    def on_execution_started(self):
        # Disable all cards
        self.bundledFileCard.setEnabled(False)
        self.installBuildToolsCard.setEnabled(False)
        self.saferCard.setEnabled(False)
        self.malwareFolderCard.setEnabled(False)
        self.keepCacheCard.setEnabled(False)
        self.makeBindiffAvailableCard.setEnabled(False)
        self.installZshCard.setEnabled(False)

    def refresh_data(self):
        self.bundledFileCard.setContent(cfg.bundledZipFile.value)
        self.installBuildToolsCard.setChecked(cfg.installBuildTools.value)
        self.saferCard.setChecked(cfg.saferEnabled.value)
        self.malwareFolderCard.setValue(cfg.malwareFolders.value)
        self.keepCacheCard.setChecked(cfg.scoopKeepCache.value)
        self.makeBindiffAvailableCard.setChecked(cfg.makeBindiffAvailable.value)
        self.installZshCard.setChecked(cfg.installZsh.value)

    # Call refresh_data every time this is opened
    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_data()
