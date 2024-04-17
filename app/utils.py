import ctypes
import glob
import os
import zipfile
import winreg
import subprocess
from pathlib import Path
from typing import List


def is_admin():
    """
    Checks if the script is running with administrative privileges.
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def create_hard_link(source, target):
    """
    Create a hard link for a file from source to target.
    """
    try:
        os.link(source, target)
    except OSError as e:
        print(f"Error creating hard link: {e}")


def link_files_and_folders(src_directory, target_directory):
    """
    Create hard links for files in src_directory to target_directory,
    and replicate the directory structure.
    """
    src_directory = Path(src_directory)
    target_directory = Path(target_directory)

    if not src_directory.is_dir():
        print(f"The source {src_directory} is not a directory.")
        return

    if not target_directory.exists():
        print(f"The target directory {target_directory} does not exist, creating it.")
        target_directory.mkdir(parents=True, exist_ok=True)

    for item in src_directory.rglob("*"):
        relative_path = item.relative_to(src_directory)
        target_path = target_directory / relative_path

        if item.is_dir():
            # Create corresponding directory in the target location
            target_path.mkdir(exist_ok=True)
        else:
            # Create a hard link for files
            create_hard_link(item, target_path)


def resolve_path(target_path):
    """
    Resolves the environment variables in the target path and returns the first matching path.
    """

    # Step 1: Expand the environment variable
    expanded_path = os.path.expandvars(target_path)

    if "*" in expanded_path:
        # Step 2: Use glob to find directories that match the wildcard pattern
        matching_paths = glob.glob(expanded_path)
    else:
        return expanded_path

    # Handling the result
    if not matching_paths:
        return None
    else:
        return matching_paths[0]


def create_start_layout_xml(apps: List[str]):
    """
    Create a Start Layout XML file with the provided apps pinned to the taskbar.
    """
    lines = []
    for app in apps:

        if app.startswith("Microsoft"):
            lines.append(f'\t\t<taskbar:DesktopApp DesktopApplicationID="{app}" />')
        else:
            app = resolve_path(app)

            lines.append(f'\t\t<taskbar:DesktopApp DesktopApplicationLinkPath="{app}" />')

    content = "\n".join(lines)

    return f'''<?xml version="1.0" encoding="utf-8"?>
<LayoutModificationTemplate
    xmlns="http://schemas.microsoft.com/Start/2014/LayoutModification"
    xmlns:defaultlayout="http://schemas.microsoft.com/Start/2014/FullDefaultLayout"
    xmlns:start="http://schemas.microsoft.com/Start/2014/StartLayout"
    xmlns:taskbar="http://schemas.microsoft.com/Start/2014/TaskbarLayout"
    Version="1">
  <CustomTaskbarLayoutCollection>
    <defaultlayout:TaskbarLayout>
      <taskbar:TaskbarPinList>
{content}
      </taskbar:TaskbarPinList>
    </defaultlayout:TaskbarLayout>
 </CustomTaskbarLayoutCollection>
</LayoutModificationTemplate>'''


def extract_zip(zip_file, target_directory):
    """
    Extract the contents of a zip file to the target directory.
    """
    # Extract the zip file
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(target_directory)


def query_registry(key_path, value_name):
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error accessing registry {key_path}: {str(e)}")
        return None

def is_service_running(service_name):
    # Using 'sc query' to check the service status
    try:
        result = subprocess.run(['sc', 'query', service_name], capture_output=True, text=True)
        if "RUNNING" in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking service status for {service_name}: {str(e)}")
        return False


def is_process_running(process_name):
    # Using 'tasklist' to check if the process is running
    try:
        result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process_name}'], capture_output=True, text=True)
        if process_name in result.stdout:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking process status for {process_name}: {str(e)}")
        return False


def is_defender_enabled():
    defender_enabled = False

    # Check various registry settings
    settings = {
        "DisableAntiSpyware": query_registry(r"SOFTWARE\Microsoft\Windows Defender", "DisableAntiSpyware"),
        "DisableAntiVirus": query_registry(r"SOFTWARE\Microsoft\Windows Defender", "DisableAntiVirus"),
        "TamperProtection": query_registry(r"SOFTWARE\Microsoft\Windows Defender\Features", "TamperProtection")
    }

    # If any key explicitly disables Defender, consider it disabled
    if settings["DisableAntiSpyware"] == 0 or settings["DisableAntiVirus"] == 0:
        defender_enabled = True

    # Check if Tamper Protection is off, which is less secure
    if settings["TamperProtection"] == 1:
        defender_enabled = True

    # Check Windows Defender services status
    services = [
        "WinDefend",      # Windows Defender Service
        "WdNisSvc"        # Windows Defender Network Inspection Service
    ]

    services_status = any(is_service_running(service) for service in services)

    if services_status:
        defender_enabled = True

    processes = [
        "MsMpEng.exe",    # Windows Defender Antivirus Service
        "NisSrv.exe"      # Windows Defender Network Inspection Service
    ]

    if any(is_process_running(process) for process in processes):
        defender_enabled = True

    # Return True only if all checks pass
    return defender_enabled


SCOOP_DIR = resolve_path(r"%USERPROFILE%\scoop")
