# coding:utf-8
# pylint: disable=E1101
import sys

from qfluentwidgets import (QConfig, ConfigItem, BoolValidator,
                            Theme)


def isWin11():
    return sys.platform == 'win32' and sys.getwindowsversion().build >= 22000


class Config(QConfig):
    """ Config of application """

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())


HELP_URL = "https://github.com/Donaldduck8/bluekit"
BUCKET_URL = "https://github.com/Donaldduck8/malware-analysis-bucket"
BLOG_URL = "https://sinkhole.dev"
FEEDBACK_URL = "https://github.com/Donaldduck8/bluekit/issues"

cfg = Config()
cfg.themeMode.value = Theme.AUTO
