# coding:utf-8
import threading

from ..common.style_sheet import StyleSheet

from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QFrame, QListWidgetItem
from qfluentwidgets import (FluentIcon, ProgressRing, InfoBar, ProgressBar, ScrollArea, ListWidget, IndeterminateProgressBar, TitleLabel)

from .. import installation_steps
from .. import utils

import logging


class ListWidgetLogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.bottomListView.addItem(msg)
        self.widget.bottomListView.scrollToBottom()


class ExecutionInterface(QWidget):
    def __init__(self, parent=None, title=None):
        super().__init__(parent)
        self.setObjectName('executionInterface' + str(id(self)))

        # Main vertical layout
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(30, 30, 30, 30)

        self.titleLabel = TitleLabel("Malware Analysis VM Setup")
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.vBoxLayout.addWidget(self.titleLabel)

        # Horizontal layout for the ProgressRing and the new ListWidget
        self.hBoxLayout = QHBoxLayout()

        # ProgressRing configuration
        self.progressRing = ProgressRing(self)
        self.progressRing.setValue(0)
        self.progressRing.setTextVisible(True)
        self.hBoxLayout.setContentsMargins(70, 30, 70, 0)
        self.hBoxLayout.addWidget(self.progressRing, alignment=Qt.AlignLeft)
        self.hBoxLayout.addSpacing(60)

        # New ListWidget to the right of the ProgressRing
        self.rightListView = ListWidget(self)
        self.rightListView.setMaximumHeight(150)
        self.hBoxLayout.addWidget(self.rightListView)

        self.hBoxLayout.setStretch(0, 0)

        # Add the horizontal layout to the main vertical layout
        self.vBoxLayout.addLayout(self.hBoxLayout)

        self.vBoxLayout.addSpacing(100)

        # Existing ListWidget at the bottom
        self.bottomListView = ListWidget(self)

        # Reduce the line spacing
        self.bottomListView.setSpacing(3)

        # Add word wrap instead of cutting off the entry
        self.bottomListView.setWordWrap(True)

        self.vBoxLayout.addWidget(self.bottomListView)
        self.vBoxLayout.addSpacing(30)

    def execute(self, data):
        print("Executing")
        installation_steps.logger.addHandler(ListWidgetLogHandler(self))
        thread = threading.Thread(target=threading_function, args=(self, data))
        thread.start()


def threading_function(widget: ExecutionInterface, data: dict):
    installation_steps.remove_worthless_python_exes()
    widget.rightListView.addItem(QListWidgetItem("Success: Removed AppAlias Python executables"))
    widget.rightListView.scrollToBottom()

    installation_steps.extract_bundled_zip()
    widget.rightListView.addItem(QListWidgetItem("Success: Extracted bundled .zip file, if present"))
    widget.rightListView.scrollToBottom()

    installation_steps.extract_scoop_cache()
    widget.rightListView.addItem(QListWidgetItem("Success: Extracted Scoop cache"))
    widget.rightListView.scrollToBottom()

    installation_steps.install_scoop()
    widget.rightListView.addItem(QListWidgetItem("Success: Installed Scoop"))
    widget.rightListView.scrollToBottom()

    installation_steps.scoop_install_git()
    widget.rightListView.addItem(QListWidgetItem("Success: Installed Git"))
    widget.rightListView.scrollToBottom()

    installation_steps.scoop_install_pwsh()
    widget.rightListView.addItem(QListWidgetItem("Success: Installed PowerShell"))
    widget.rightListView.scrollToBottom()

    installation_steps.scoop_add_buckets(data["scoop"]["Buckets"])
    widget.rightListView.addItem(QListWidgetItem("Success: Added Scoop buckets"))
    widget.rightListView.scrollToBottom()

    installation_steps.scoop_install_tooling(data["scoop"])
    widget.rightListView.addItem(QListWidgetItem("Success: Installed Scoop tooling"))
    widget.rightListView.scrollToBottom()

    installation_steps.pip_install_packages(data["pip"])
    widget.rightListView.addItem(QListWidgetItem("Success: Installed pip packages"))
    widget.rightListView.scrollToBottom()

    installation_steps.npm_install_libraries(data["npm"])
    widget.rightListView.addItem(QListWidgetItem("Success: Installed npm libraries"))
    widget.rightListView.scrollToBottom()

    installation_steps.install_ida_plugins(data["ida_plugins"])
    widget.rightListView.addItem(QListWidgetItem("Success: Installed IDA Pro plugins"))
    widget.rightListView.scrollToBottom()

    installation_steps.set_file_type_associations(data["file_type_associations"])
    widget.rightListView.addItem(QListWidgetItem("Success: Set file type associations"))
    widget.rightListView.scrollToBottom()

    installation_steps.pin_apps_to_taskbar(data["taskbar_pins"])
    widget.rightListView.addItem(QListWidgetItem("Success: Pinned apps to taskbar"))
    widget.rightListView.scrollToBottom()

    installation_steps.clone_git_repositories(data["git_repositories"])
    widget.rightListView.addItem(QListWidgetItem("Success: Cloned Git repositories"))
    widget.rightListView.scrollToBottom()

    # Run IDAPySwitch to ensure that IDA Pro works immediately after installation
    installation_steps.ida_py_switch(data["ida_py_switch"])
    widget.rightListView.addItem(QListWidgetItem("Success: Ran IDAPySwitch"))
    widget.rightListView.scrollToBottom()

    # Make Bindiff available to other programs
    installation_steps.make_bindiff_available_to_programs()
    widget.rightListView.addItem(QListWidgetItem("Success: Made BinDiff available to other programs"))
    widget.rightListView.scrollToBottom()

    # Install Zsh on top of git
    installation_steps.install_zsh_over_git()
    widget.rightListView.addItem(QListWidgetItem("Success: Installed Zsh over Git"))
    widget.rightListView.scrollToBottom()

    # Install Recaf3's JavaFX dependencies to ensure it works even if VM is not connected to the internet
    installation_steps.extract_and_place_file("recaf3_javafx_dependencies.zip", utils.resolve_path(r"%APPDATA%\Recaf\dependencies"))
    widget.rightListView.addItem(QListWidgetItem("Success: Installed Recaf3's JavaFX dependencies"))
    widget.rightListView.scrollToBottom()

    # Add Npcap's annoying non-silent installer to the RunOnce registry key
    installation_steps.add_npcap_installer_to_runonce()
    widget.rightListView.addItem(QListWidgetItem("Success: Added Npcap installer to RunOnce"))
    widget.rightListView.scrollToBottom()

    # Install .NET 3.5, which is required by some older malware samples
    installation_steps.install_net_3_5()
    widget.rightListView.addItem(QListWidgetItem("Success: Installed .NET 3.5"))
    widget.rightListView.scrollToBottom()

    installation_steps.obtain_and_place_malware_analysis_configurations()
    widget.rightListView.addItem(QListWidgetItem("Success: Obtained and placed malware analysis configurations"))
    widget.rightListView.scrollToBottom()

    installation_steps.enable_dark_mode()
    widget.rightListView.addItem(QListWidgetItem("Success: Enabled dark mode"))
    widget.rightListView.scrollToBottom()

    installation_steps.common_post_install()
    widget.rightListView.addItem(QListWidgetItem("Success: Common post-installation steps"))
    widget.rightListView.scrollToBottom()

    installation_steps.clean_up_disk()
    widget.rightListView.addItem(QListWidgetItem("Success: Cleaned up disk"))
    widget.rightListView.scrollToBottom()

    '''
    for i in range(100):
        if not widget.progressRing.paintingActive():
            widget.progressRing.setValue(i)
        widget.rightListView.addItem(QListWidgetItem("Item " + str(i)))
        widget.bottomListView.addItem(QListWidgetItem("Item " + str(i)))
        widget.bottomListView.scrollToBottom()
        widget.rightListView.scrollToBottom()
        import time
        time.sleep(0.5)
    '''
