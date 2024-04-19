# coding:utf-8
import ctypes
import json5
import os
import sys
import traceback
import argparse

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from app import installation_steps, utils
from app.common.config import cfg
from app.view.main_window import MainWindow
from data import required_paths, data

try:
    import pyi_splash
except ImportError:
    pyi_splash = None

parser = argparse.ArgumentParser(
    prog='Bluekit',
    description='A cybersecurity-focused workstation setup script',
    epilog='Have fun!'
)

parser.add_argument('-s', '--silent', action='store_true', help='Run the script without any GUI prompts')


def run_gui():
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

    if pyi_splash:
        pyi_splash.close()

    # create main window
    w = MainWindow()
    w.show()

    app.exec_()


def ensure_suitable_environment():
    # If we are frozen
    if getattr(sys, "frozen", False):
        # If Windows Defender is enabled, show an error message
        if utils.is_defender_enabled():
            if pyi_splash:
                pyi_splash.close()

            ctypes.windll.user32.MessageBoxW(
                0,
                "Windows Defender is or was enabled. Proceeding with the installation may cause Windows Defender to delete some files, or the installation to fail outright.",
                "Windows Defender",
                0x1,
            )

        # Add the paths to the PATH environment variable
        installation_steps.add_paths_to_path(required_paths)

        if not utils.is_admin():
            # Not running as admin, try to get admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()


def main():
    ensure_suitable_environment()

    args = parser.parse_args()

    if args.silent:
        if pyi_splash:
            pyi_splash.close()

        installation_steps.install_bluekit(data)

    else:
        run_gui()


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        # Show the error message box using windows message box API
        if pyi_splash:
            pyi_splash.close()

        exception_traceback = traceback.format_exc(e)
        ctypes.windll.user32.MessageBoxW(0, exception_traceback, "Error", 0x10)
