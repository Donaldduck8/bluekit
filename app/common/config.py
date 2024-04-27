# coding:utf-8
# pylint: disable=E1101
import sys
import types

from pathlib import Path

from qfluentwidgets import BoolValidator, ConfigItem, ConfigValidator
from qfluentwidgets.common.config import QConfig


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class ZipFileValidator(ConfigValidator):
    """ .ZIP file validator """

    def validate(self, value):
        result = Path(value).exists() and Path(value).is_file() and Path(value).suffix == ".zip"
        return result

    def correct(self, value):
        return value


class Config(QConfig):
    """ Config of application """

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())

    saferEnabled = ConfigItem("Safer", "SaferEnabled", True, BoolValidator())
    malwareFolders = ConfigItem(
        "Safer", "malwareFolders", [], None)

    makeBindiffAvailable = ConfigItem("Bindiff", "MakeBindiffAvailable", True, BoolValidator())

    scoopKeepCache = ConfigItem("Scoop", "KeepCache", False, BoolValidator())

    installZsh = ConfigItem("Scoop", "InstallZsh", True, BoolValidator())

    bundledZipFile = ConfigItem("BundledFiles", "BundledZipFile", "", ZipFileValidator())

    installBuildTools = ConfigItem("BuildTools", "InstallBuildTools", True, BoolValidator())


HELP_URL = "https://github.com/Donaldduck8/bluekit"
BUCKET_URL = "https://github.com/Donaldduck8/malware-analysis-bucket"
BLOG_URL = "https://sinkhole.dev"
FEEDBACK_URL = "https://github.com/Donaldduck8/bluekit/issues"

cfg = Config()


# Monkey-patch save method
def save(_self):
    pass


cfg.save = types.MethodType(save, QConfig)  # pylint: disable=attribute-defined-outside-init
