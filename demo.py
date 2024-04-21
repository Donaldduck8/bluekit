# coding:utf-8
import argparse
import ctypes
import os
import sys
import traceback

from pathlib import Path

import json5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

import data
from app import installation_steps, utils
from app.view.main_window import MainWindow

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
parser.add_argument('-c', '--config', help='Path to the configuration file', type=Path)
args = parser.parse_args()


def run_gui():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # create application
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

    if pyi_splash and pyi_splash.is_alive():
        pyi_splash.close()

    # create main window
    w = MainWindow()
    w.show()

    app.exec_()


def ensure_suitable_environment():
    # If we are frozen
    if getattr(sys, "frozen", False):
        # Add the paths to the PATH environment variable
        installation_steps.add_paths_to_path(data.required_paths)

        if not utils.is_admin():
            # Not running as admin, try to get admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()


def load_config(config_p: str):
    if not os.path.isfile(config_p):
        raise FileNotFoundError(f"Config file not found: {config_p}")

    with open(config_p, 'r', encoding="utf-8") as config_file:
        custom_data = json5.loads(config_file.read())

    # Perform validation on the custom data
    for top_level_keys in custom_data.keys():
        if top_level_keys not in data.default_configuration.keys():
            raise KeyError(f"Unrecognized key in custom configuration: {top_level_keys}")
        
    data.validate_configuration(custom_data, data.default_configuration)
    data.configuration = custom_data


def main():
    ensure_suitable_environment()

    if args.config:
        load_config(args.config)

    if args.silent:
        if pyi_splash:
            pyi_splash.close()

        installation_steps.install_bluekit(data.configuration)

    else:
        run_gui()


if __name__ == "__main__":
    try:
        main()

    except Exception as e:
        if pyi_splash and pyi_splash.is_alive():
            pyi_splash.close()

        exception_traceback = traceback.format_exc()
        ctypes.windll.user32.MessageBoxW(0, exception_traceback, "Error", 0x10)
