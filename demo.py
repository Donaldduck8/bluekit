# coding:utf-8
import os
import sys
import ctypes
import traceback

from app import utils
from app import installation_steps

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from app.common.config import cfg
from app.view.main_window import MainWindow

from data import required_paths


def main():
    # Ensure that the required paths are in the PATH environment variable

    # If we are frozen
    if getattr(sys, "frozen", False):
        # Add the paths to the PATH environment variable
        installation_steps.add_paths_to_path(required_paths)

        if not utils.is_admin():
            # Not running as admin, try to get admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()

    # enable dpi scale
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    # create main window
    w = MainWindow()
    w.show()

    app.exec_()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        exception_traceback = traceback.format_exc()
        # Show the error message box using windows message box API
        ctypes.windll.user32.MessageBoxW(0, exception_traceback, "Error", 0x10)
