# coding:utf-8
import ctypes
import json5
import logging
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
                    epilog='Have fun!')

parser.add_argument('-s', '--silent', action='store_true', help='Run the script without any GUI prompts')


def main():
    # If we are frozen
    if getattr(sys, "frozen", False):
        # If Windows Defender is enabled, show an error message
        if utils.is_defender_enabled():
            if pyi_splash:
                pyi_splash.close()

            ctypes.windll.user32.MessageBoxW(
                0,
                "Windows Defender is enabled. Please disable it before running BlueKit.\n\nThe author strongly recommends building a custom Windows image with Windows Defender removed using tools like NtLite or tiny11builder.",
                "Error",
                0x10,
            )
            sys.exit()

        # Add the paths to the PATH environment variable
        installation_steps.add_paths_to_path(required_paths)

        if not utils.is_admin():
            # Not running as admin, try to get admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()

    args = parser.parse_args()

    if args.silent:
        if pyi_splash:
            pyi_splash.close()

        installation_steps.common_pre_install()
        installation_steps.remove_worthless_python_exes()
        installation_steps.extract_bundled_zip()
        installation_steps.extract_scoop_cache()

        installation_steps.install_scoop()
        installation_steps.scoop_install_git()

        installation_steps.scoop_install_pwsh()

        installation_steps.scoop_add_buckets(data["scoop"]["Buckets"])
        installation_steps.scoop_install_tooling(data["scoop"])
        installation_steps.pip_install_packages(data["pip"])
        installation_steps.npm_install_libraries(data["npm"])
        installation_steps.install_ida_plugins(data["ida_plugins"])
        installation_steps.set_file_type_associations(data["file_type_associations"])
        installation_steps.pin_apps_to_taskbar(data["taskbar_pins"])
        installation_steps.clone_git_repositories(data["git_repositories"])
        installation_steps.make_registry_changes(data["registry_changes"])

        # Run IDAPySwitch to ensure that IDA Pro works immediately after installation
        installation_steps.ida_py_switch(data["ida_py_switch"])

        # Make Bindiff available to other programs
        installation_steps.make_bindiff_available_to_programs()

        # Install Zsh on top of git
        installation_steps.install_zsh_over_git()

        # Install Recaf3's JavaFX dependencies to ensure it works even if VM is not connected to the internet
        installation_steps.extract_and_place_file("recaf3_javafx_dependencies.zip", utils.resolve_path(r"%APPDATA%\Recaf\dependencies"))

        # Install .NET 3.5, which is required by some older malware samples
        # installation_steps.install_net_3_5()
        # widget.rightListView.listWidget.add_infobar_signal.emit("Success: Installed .NET 3.5", "", InfoBarIcon.SUCCESS)
        # widget.rightListView.listWidget.scrollToBottom()

        installation_steps.obtain_and_place_malware_analysis_configurations()
        installation_steps.common_post_install()
        installation_steps.clean_up_disk()

    else:
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


if __name__ == "__main__":
    try:
        with open('log.txt', 'w', encoding="utf-8") as log_f:
            sys.stdout = log_f
            sys.stderr = log_f
            installation_steps.logger.addHandler(logging.StreamHandler(sys.stdout))
            installation_steps.logger.addHandler(logging.StreamHandler(sys.stderr))
            installation_steps.logger.setLevel(logging.DEBUG)
            main()

            sys.stdout = sys.__stdout__
        
    except Exception:
        # Show the error message box using windows message box API
        exception_traceback = traceback.format_exc()
        ctypes.windll.user32.MessageBoxW(0, exception_traceback, "Error", 0x10)
