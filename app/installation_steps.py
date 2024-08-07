# pylint: disable=E1101
"""
This module contains functions for performing various installation steps.

The functions in this module are used to execute shell commands, install Scoop package manager,
install Git using Scoop, add Scoop buckets, install Python packages using pip, install Visual C++ build tools,
and install tools using Scoop package manager.
"""

import ctypes
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import traceback
import uuid
import winreg
from collections import OrderedDict
from dataclasses import asdict
from typing import List

import pythoncom
import win32com.client
from qfluentwidgets import InfoBarIcon

from app import data, utils
from app.common.config import cfg

HERE = os.path.dirname(os.path.abspath(__file__))

if "_MEI" in HERE and getattr(sys, "frozen", False):
    # We are in a PyInstaller bundle, but I want the location of the PyInstaller executable
    HERE = os.path.dirname(sys.executable)

log_p = os.path.join(HERE, "install.log")
errors_p = os.path.join(HERE, "errors.log")
configuration_out_p = os.path.join(HERE, "configuration_dump.json")


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=log_p,
                    filemode="a")
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))

widget = None


def try_log_installation_step(message: str, icon: InfoBarIcon = InfoBarIcon.INFORMATION):
    """
    Logs an installation step.

    Args:
        message (str): The message to log.
        icon (InfoBarIcon, optional): The icon to use. Defaults to InfoBarIcon.INFORMATION.
    """
    try:
        if widget:
            widget.rightListView.listWidget.add_infobar_signal.emit(message, "", icon)
    except Exception:
        pass


def get_registry_environment(key_handle, sub_key):
    """Retrieve environment variables from Windows Registry."""
    environment = {}
    try:
        with winreg.OpenKey(key_handle, sub_key) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    environment[name] = value
                    i += 1
                except Exception:
                    break
    except Exception as e:
        print(f"Failed to open registry key: {e}")
    return environment


def update_environment_from_registry():  # pylint: disable=too-many-branches
    # Get system and user environment variables from registry
    # system_env = get_registry_environment(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
    user_env = get_registry_environment(winreg.HKEY_CURRENT_USER, r"Environment")

    for k,v in user_env.items():
        if isinstance(v, list):
            v_new = []

            for x in v:
                if utils.resolve_path(x) is not None:
                    v_new.append(utils.resolve_path(x))
                else:
                    v_new.append(x)

        else:
            if utils.resolve_path(v) is not None:
                v_new = utils.resolve_path(v)
            else:
                v_new = v

        v_str = ";".join(v) if isinstance(v, list) else v

        existing = os.getenv(k)

        if existing is None:
            new_value = v
        else:
            new_value = f"{existing};{v_str}"

        # Deduplicate new value
        new_value = ";".join(list(OrderedDict.fromkeys(new_value.split(";"))))

        os.environ[k] = new_value

    # Go through each item again and if the item is actually just another environment variable, resolve it
    for k,v in os.environ.items():
        v_items = v.split(";")
        v_items_new = []

        for v_item in v_items:
            if v_item.startswith("%") and v_item.endswith("%") and v_item[1:-1] in os.environ:
                v_items_new.append(os.environ[v_item[1:-1]])
            else:
                v_items_new.append(v_item)

        os.environ[k] = ";".join(v_items_new)

    # Make TMP and TEMP each a single path
    if "TMP" in os.environ:
        os.environ["TMP"] = os.environ["TMP"].split(";")[0]

    if "TEMP" in os.environ:
        os.environ["TEMP"] = os.environ["TEMP"].split(";")[0]

    # Run a single PowerShell script for all environment variables
    commands = [f'[Environment]::SetEnvironmentVariable("{k}", "{os.environ[k]}", "Machine")' for k, _ in user_env.items()]
    commands_joined = ";\n".join(commands)
    subprocess.run(["powershell", "-Command", "$(" + commands_joined + ")"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def format_output(stream: bytes):
    """
    Formats the output of a subprocess.

    Args:
        stream (bytes): The output stream to format.

    Returns:
        str: The formatted output.
    """
    temp = stream.decode("utf-8", errors="replace").strip()

    while ("\r\n\r\n" in temp) or ("\n\n" in temp) or ("\r\r" in temp):
        temp = temp.replace("\r\n\r\n", "\r\n").replace("\n\n", "\n").replace("\r\r", "\r")

    if not temp.endswith("\n"):
        temp += "\n"

    return temp.strip()


def run_shell_command(command: str = None, powershell_command: str = None, command_parts: List[str] = None, failure_okay: bool = False, total_attempts: int = 3, needs_refresh: bool = False) -> None:  # pylint: disable=too-many-branches
    """
    Executes a shell command or a PowerShell command.

    Args:
        command (str, optional): The shell command to execute. Defaults to None.
        powershell_command (str, optional): The PowerShell command to execute. Defaults to None.
        command_parts (List[str], optional): The command parts to execute. Defaults to None.
        failure_okay (bool, optional): Whether failure is allowed. Defaults to False.
        total_attempts (int, optional): The total number of attempts to make. Defaults to 3.
    Returns:
        None
    Raises:
        Exception: If the command execution fails and failure_okay is False.
    """
    for attempt_number in range(total_attempts):
        try:
            if command:
                logger.info(f"Shell: '{command}'")
                p = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

            elif powershell_command:
                logger.info(f"PowerShell: '{powershell_command}'")
                p = subprocess.run([r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", "-Command", "$(" + powershell_command + ")"],
                                   check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            elif command_parts:
                logger.info(f"Shell: '{json.dumps(command_parts)}'")
                p = subprocess.run(command_parts, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            else:
                raise ValueError("No command provided.")

            if p.returncode != 0:
                raise subprocess.CalledProcessError(p.returncode, p.args, p.stdout, p.stderr)

            stdout = format_output(p.stdout)
            stderr = format_output(p.stderr)

            if len(stdout) > 0:
                logger.info(stdout)

            if len(stderr) > 0:
                logger.info(stderr)

            break

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to run command: {e.cmd}")
            if e.stdout:
                stdout = format_output(e.stdout)
                logger.warning(f"Output: {stdout}")

                with open(errors_p, "a+", encoding="utf-8") as f:
                    f.write(stdout)

            if e.stderr:
                stderr = format_output(e.stderr)
                logger.warning(f"Output: {stderr}")

                with open(errors_p, "a+", encoding="utf-8") as f:
                    f.write(stderr)

            if not failure_okay and attempt_number >= total_attempts - 1:
                raise e
        except Exception as e:
            trace = traceback.format_exc()
            logger.warning(f"Failed to run command: {trace}")

            with open(errors_p, "a+", encoding="utf-8") as f:
                f.write(trace + "\n")

            if not failure_okay and attempt_number >= total_attempts - 1:
                raise e

    if needs_refresh:
        update_environment_from_registry()


def install_scoop() -> None:
    """
    Installs Scoop package manager if it is not already installed.
    """
    logger.info("Installing Scoop")

    # Check if scoop is already installed
    if shutil.which("scoop.cmd") is not None:
        logger.info("Scoop is already installed.")

        try_log_installation_step("Info: Scoop is already installed", InfoBarIcon.INFORMATION)

        return

    install_script_p = os.path.join(HERE, "install_scoop.ps1")

    command = f"""
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Invoke-RestMethod -Uri https://raw.githubusercontent.com/scoopinstaller/install/master/install.ps1 -O {install_script_p}
    {install_script_p} -RunAsAdmin
    """

    run_shell_command(powershell_command=command, needs_refresh=True)

    try_log_installation_step("Success: Installed Scoop", InfoBarIcon.SUCCESS)


def scoop_install_git() -> None:
    """
    Explicitly installs Git using Scoop package manager.

    Git is required for various operations, such as updating Scoop or adding buckets, so an explicit installation is nice-to-have.
    """
    logger.info("Scoop: Install Git")

    run_shell_command(command="scoop.cmd install git", needs_refresh=True)

    try_log_installation_step("Success: Installed Git", InfoBarIcon.SUCCESS)


def scoop_add_buckets(buckets: List[data.BasePackageStructure]):
    """
    Adds Scoop buckets to the package manager.

    Args:
        buckets (List[str]): A list of bucket names to add.

    Returns:
        None
    """
    logger.info("Scoop: Add buckets")

    for bucket in buckets:
        bucket_id = bucket.id
        bucket_command = bucket_id

        if " " in bucket_id:
            bucket_id = bucket_id.split(" ")[0]

        run_shell_command(command=f"scoop.cmd bucket add {bucket_command}")

        # Double-check if the bucket was added successfully, since this shit likes to fucking fail
        bucket_p = utils.resolve_path(f"%USERPROFILE%\\scoop\\buckets\\{bucket_id}")
        bucket_bucket_p = utils.resolve_path(f"%USERPROFILE%\\scoop\\buckets\\{bucket_id}\\bucket")

        retry = 0

        while not os.path.isdir(bucket_bucket_p):
            logger.warning("Bucket did not download correctly: " + bucket_p)

            if retry >= 5:
                # Show error message box
                ctypes.windll.user32.MessageBoxW(
                    0,
                    f"Could not add Scoop bucket {bucket.name} despite repeated attempts.",
                    "Error",
                    0x10,
                )
                raise RuntimeError(f"Could not add Scoop bucket {bucket.name}.")

            if os.path.isdir(bucket_p):
                run_shell_command(command=f"scoop.cmd bucket rm {bucket_id}")

            run_shell_command(command=f"scoop.cmd bucket add {bucket_command}")

            retry += 1

    try_log_installation_step("Success: Added Scoop buckets", InfoBarIcon.SUCCESS)


def pip_install_packages(packages: List[data.PipPackage]):
    """
    Installs Python packages using pip.

    Args:
        packages (List[data.PipPackage]): A list of Python packages to install.

    Returns:
        None
    """
    logger.info("PIP: Install packages")

    run_shell_command(command="pip.exe install --upgrade pipx", failure_okay=False)

    for package in packages:
        package_id = package.id
        package_name = package.name

        if package.mode == "pip":
            run_shell_command(command=f"pip.exe install {package_id}", failure_okay=True)
            try_log_installation_step(f"Success: Installed {package_name} (PIP)", InfoBarIcon.SUCCESS)

        elif package.mode == "pipx":
            run_shell_command(command=f"pipx.exe install {package_id}", failure_okay=True)
            try_log_installation_step(f"Success: Installed {package_name} (PIPX)", InfoBarIcon.SUCCESS)

        else:
            try_log_installation_step("Warning: PIP package mode is unknown, skipping!", InfoBarIcon.WARNING)


def install_build_tools():
    """
    Silently installs Visual C++ build tools using the Visual Studio installer.
    """
    logger.info("Install Visual C++ build tools")

    download_command = r"Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vs_BuildTools.exe' -OutFile vs_BuildTools.exe"
    install_command = " ".join([
        "vs_BuildTools.exe --passive --wait",
        "--add Microsoft.VisualStudio.Workload.VCTools",
        "--includeRecommended",
        "--remove Microsoft.VisualStudio.Component.VC.CMake.Project",
        "--remove Microsoft.VisualStudio.Component.TestTools.BuildTools",
        "--remove Microsoft.VisualStudio.Component.VC.ASAN"
    ])

    run_shell_command(powershell_command=download_command)
    run_shell_command(command=install_command)

    try_log_installation_step("Success: Installed Visual C++ Build Tools", InfoBarIcon.SUCCESS)


def scoop_install_tool(tool_name: str, tool_name_pretty: str = None, keep_cache: bool = False):
    """
    Installs a tool using Scoop package manager.

    Args:
        tool_name (str): The name of the tool to install.

    Returns:
        bool: If the tool installed successfully or not.
    """
    if tool_name_pretty is None:
        tool_name_pretty = tool_name
    logger.info(f"Scoop: Install '{tool_name_pretty}'")

    try:
        if tool_name.endswith(".json"):
            tool_name = tool_name[:-5]

            if not extract_and_install_application(tool_name):
                return False
        else:
            run_shell_command(command=f"scoop.cmd install {tool_name}", needs_refresh=True)

    except Exception:
        traceback.print_exc()
        logger.warning(f"Failed to install {tool_name}, skipping...")
        return False

    if not keep_cache:
        # If the tool_name contains the bucket, we need to strip that
        if "/" in tool_name:
            tool_name = tool_name.split("/")[-1]

        run_shell_command(command=f"scoop.cmd cache rm {tool_name}")

    return True


def scoop_install_tooling(tools: dict[str, list[data.ScoopPackage]], install_context=True, install_associations=True, keep_cache=False):
    """
    Installs tools using Scoop package manager.
    """
    logger.info("Scoop: Install Tooling")

    for _category, packages in tools.items():
        if not isinstance(packages, list):
            logger.warning("Data is not list, skipping...")

            try_log_installation_step("Warning: Scoop data is not a list, skipping!", InfoBarIcon.WARNING)

            continue

        for package in packages:
            if not isinstance(package, data.ScoopPackage):
                logger.warning("Package is not ScoopPackage, skipping...")

                try_log_installation_step("Warning: Scoop package is not ScoopPackage, skipping!", InfoBarIcon.WARNING)

                continue

            package_id = package.id
            package_name = package.name

            if not scoop_install_tool(package_id, package_name, keep_cache=keep_cache):
                if package.alternative is not None:
                    package_id = package.alternative.id
                    package_name = package.alternative.name

                    scoop_install_tool(package_id, package_name, keep_cache=keep_cache)

            # Install context menu items and file associations
            package_dir = os.path.join(utils.SCOOP_DIR, "apps", package_id, "current")

            package_context_reg_p = os.path.join(package_dir, "install-context.reg")
            package_file_associations_reg_p = os.path.join(package_dir, "install-file-associations.reg")

            python_reg_p = os.path.join(package_dir, "install-pep-514.reg")

            if install_context and os.path.isfile(package_context_reg_p):
                run_shell_command(f"regedit /s {package_context_reg_p}")

            if install_associations and os.path.isfile(package_file_associations_reg_p):
                run_shell_command(f"regedit /s {package_file_associations_reg_p}")

            if os.path.isfile(python_reg_p):
                run_shell_command(f"regedit /s {python_reg_p}")

            try_log_installation_step(f"Success: Installed {package_name}", InfoBarIcon.SUCCESS)


def prepare_quick_access():
    """
    Pins the user folder to Quick Access and unpins all other items.
    """
    logger.info("Prepare the Quick Access folder")

    # Required to use COM objects in a multi-threaded environment
    pythoncom.CoInitialize()

    # Function to pin a folder to Quick Access
    def pin_to_quick_access(path):
        shell = win32com.client.Dispatch("Shell.Application")
        namespace = shell.NameSpace(path)
        folder = namespace.Self
        folder.InvokeVerb("pintohome")

    # Function to unpin all items from Quick Access except the specified folder
    def unpin_all_except(path):
        quick_access_path = r"shell:::{679f85cb-0220-4080-b29b-5540cc05aab6}"
        shell = win32com.client.Dispatch("Shell.Application")
        namespace = shell.NameSpace(quick_access_path)
        item = namespace.Self

        for i in range(namespace.Items().Count - 1, -1, -1):
            item = namespace.Items().Item(i)
            if item.Path != os.path.abspath(path):
                item.InvokeVerb("unpinfromhome")
                item.InvokeVerb("removefromhome")

    # Specify the user folder path you want to pin to Quick Access
    user_folder_path = os.path.expanduser("~")

    # Pin the user folder to Quick Access
    pin_to_quick_access(user_folder_path)

    # Unpin all other items from Quick Access except the user folder
    unpin_all_except(user_folder_path)


def install_vscode_extensions(extensions: List[data.VscodeExtension]):
    """
    Installs Visual Studio Code extensions using the Code/Codium command line.
    """
    vscode_cmd_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\vscode\current\bin\code.cmd")
    vscodium_cmd_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\vscodium\current\bin\codium.cmd")

    for extension in extensions:
        extension_id = extension.id
        extension_name = extension.name

        if os.path.isfile(vscode_cmd_p):
            run_shell_command(command=f"{vscode_cmd_p} --install-extension {extension_id}", failure_okay=True)

            try_log_installation_step(f"Success: Installed {extension_name} (VS Code)", InfoBarIcon.SUCCESS)

        if os.path.isfile(vscodium_cmd_p):
            run_shell_command(command=f"{vscodium_cmd_p} --install-extension {extension_id}", failure_okay=True)

            try_log_installation_step(f"Success: Installed {extension_name} (VSCodium)", InfoBarIcon.SUCCESS)


def remove_taskbar_pin(app_name):
    """
    Removes a pinned item from the taskbar.

    Args:
        app_name (str): The name of the application to remove from the taskbar.

    Returns:
        None
    """
    logger.info(f"Remove from Taskbar: '{app_name}'")

    command = "\n".join([
        f'$appName = "{app_name}"',

        '$taskbarNamespace = (New-Object -Com Shell.Application).NameSpace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}")',

        '$pinnedItem = $taskbarNamespace.Items() | Where-Object { $_.Name -eq $appName }',

        'if ($pinnedItem) {',
        '   $pinnedItem.Verbs() | Where-Object { $_.Name.replace(\'&\', \'\') -match \'Unpin from taskbar\' } | ForEach-Object { $_.DoIt() }',
        '   Write-Host "Successfully unpinned \'$appName\' from the taskbar."',
        '} else {',
        '   Write-Host "The application \'$appName\' is not currently pinned to the taskbar."',
        '}',
    ])

    run_shell_command(powershell_command=command, failure_okay=True)


def pin_apps_to_taskbar(taskbar_pins: List[data.TaskbarPin]):
    """
    Pins applications to the taskbar using a startLayout.xml file.

    The startLayout.xml file is created with the specified apps and takes effect on the next login.
    """
    app_paths = []

    for taskbar_pin in taskbar_pins:
        app_paths.append(taskbar_pin.id)

    xml_content = utils.create_start_layout_xml(apps=app_paths)
    xml_p = utils.resolve_path(r"%USERPROFILE%\Documents\startLayout.xml")

    with open(xml_p, "w+", encoding="UTF-8") as xml_f:
        xml_f.write(xml_content)

    try_log_installation_step("Success: Created taskbar configuration", InfoBarIcon.SUCCESS)


def make_vm_stay_awake():
    """
    Disables sleep mode and hibernation on the VM using powercfg.
    """
    logger.info("Make VM stay awake")

    ps_script = "\n".join([
        # Disable Hibernation
        "powercfg /h off",

        # Set the sleep timeout to 0 to disable sleep mode for both AC and battery
        "powercfg -change -standby-timeout-ac 0",
        "powercfg -change -standby-timeout-dc 0",

        # Optional: Disable turning off of display
        "powercfg -change -monitor-timeout-ac 0",
        "powercfg -change -monitor-timeout-dc 0",

        # Optional: Set High Performance power plan
        "$highPerfPlan = powercfg -list | Select-String 'High performance' -Context 0,1",
        '$highPerfPlan = ($highPerfPlan -split "`n")[0]',
        "if($highPerfPlan -ne $null) {",
        "    $highPerfPlanGUID = $highPerfPlan -replace \".*?: (.*  ).*\", '$1'",
        "    powercfg /S $highPerfPlanGUID.Trim()",
        "}"
    ])

    # Execute the PowerShell script
    run_shell_command(powershell_command=ps_script, failure_okay=True)

    try_log_installation_step("Success: Disabled standby mode", InfoBarIcon.SUCCESS)


def common_pre_install():
    """
    Executes common pre-installation tasks.
    """
    logger.info("Common pre-installation steps")

    functions = [
        make_vm_stay_awake,
    ]

    for function in functions:
        try:
            function()
        except Exception:
            traceback.print_exc()


def common_post_install():
    """
    Executes common post-installation tasks.
    """
    logger.info("Common post-installation steps")

    functions = [
        prepare_quick_access,
        remove_taskbar_pin("Microsoft Store"),
        remove_taskbar_pin("Microsoft Edge"),
        make_scoop_buckets_safe,
    ]

    for function in functions:
        try:
            function()
        except Exception:
            traceback.print_exc()

    try_log_installation_step("Success: Common post-installation steps", InfoBarIcon.SUCCESS)


def restart():
    """
    Restarts the system.
    """
    run_shell_command(powershell_command="Restart-Computer", failure_okay=True)


def make_scoop_buckets_safe():
    """
    Adds the Scoop buckets to the safe directories list in git config.
    """
    logger.info("Make Scoop buckets safe")

    # Since this installer is run as admin, some file ownership nonsense is happening.
    # This function adds the buckets to the safe directories list in git config.
    buckets_dir = utils.resolve_path(r"%USERPROFILE%\scoop\buckets")
    for entry in os.listdir(buckets_dir):
        entry_p = os.path.join(buckets_dir, entry)

        if not os.path.isdir(entry_p):
            continue

        entry_p = entry_p.replace('\\', '/')

        run_shell_command(command=f"git.exe config --global --add safe.directory {entry_p}")


def extract_and_install_application(application_name: str):
    """
    Extracts and installs an application using Scoop package manager.

    Args:
        application_name (str): The name of the application to extract and install.

    Returns:
        None
    """
    logger.info(f"Extract and install bundled application: '{application_name}'")

    appdata_temp_p = utils.resolve_path(r"%LOCALAPPDATA%\Temp")

    application_zip_p = os.path.join(appdata_temp_p, f"{application_name}.zip")
    application_json_p = os.path.join(appdata_temp_p, f"{application_name}.json")

    if not os.path.isfile(application_zip_p) or not os.path.isfile(application_json_p):
        logger.warning("Required files not found, skipping...")
        return False

    # Load the JSON file
    with open(application_json_p, "r", encoding="utf-8") as application_json_f:
        scoop_data = json.loads(application_json_f.read())

    # Point the scoop URL at the extracted ZIP file
    scoop_data["url"] = "file://" + application_zip_p.replace("\\", "/")

    # Replace the hash with the correct one
    with open(application_zip_p, "rb") as application_zip_f:
        application_hash = hashlib.sha256(application_zip_f.read()).hexdigest()

    scoop_data["hash"] = application_hash

    # Write the JSON file back
    with open(application_json_p, "w", encoding="utf-8") as application_json_f:
        application_json_f.write(json.dumps(scoop_data, indent=4))

    # Install the application
    run_shell_command(f"scoop.cmd install {application_json_p}")

    return True


def extract_and_place_file(file_name: str, target_directory: str, extract: bool = False):
    """
    Extracts and places all contents of a .zip file to a target directory.
    """
    logger.info(f"Extract and place bundled file '{file_name}' to '{target_directory}'")

    appdata_temp_p = utils.resolve_path(r"%LOCALAPPDATA%\Temp")
    file_p = os.path.join(appdata_temp_p, f"{file_name}")

    if not os.path.isfile(file_p):
        logger.warning("File not found, skipping...")
        return

    target_directory = utils.resolve_path(target_directory)
    os.makedirs(target_directory, exist_ok=True)

    if extract:
        utils.extract_zip(file_p, target_directory)
    else:
        shutil.copy(file_p, target_directory)


def clean_up_disk(keep_cache: bool = False):
    """
    Cleans up the disk by deleting temporary files and caches.
    """

    def delete_everything_recursively_in_directory(directory):
        """
        Deletes everything recursively in a directory.

        Args:
            directory (str): The directory to clean up.

        Returns:
            None
        """
        for root, dirs, files in os.walk(directory):
            for file_to_delete in files:
                try:
                    os.unlink(os.path.join(root, file_to_delete))
                except Exception:
                    pass
            for directory_to_delete in dirs:
                try:
                    shutil.rmtree(os.path.join(root, directory_to_delete))
                except Exception:
                    pass

    cache_dir = utils.resolve_path(r"%USERPROFILE%\scoop\cache")
    temp_dir = utils.resolve_path(r"%LOCALAPPDATA%\Temp")
    software_distribution_dir = utils.resolve_path(r"C:\Windows\SoftwareDistribution\Download")
    windows_temp_dir = utils.resolve_path(r"C:\Windows\Temp")
    random_cache_dir = utils.resolve_path(r"C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache")
    package_cache_dir = r"C:\ProgramData\Package Cache"

    folders = [
        temp_dir,
        software_distribution_dir,
        windows_temp_dir,
        random_cache_dir,
        package_cache_dir
    ]

    if not keep_cache:
        folders.append(cache_dir)

    for folder in folders:
        delete_everything_recursively_in_directory(folder)

    # subprocess.run("Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase".split(" "), check=True)

    try_log_installation_step("Success: Cleaned up disk", InfoBarIcon.SUCCESS)


def extract_scoop_cache(cache_name: str = "scoop_cache") -> bool:
    """
    Extracts a .zip file to the Scoop cache directory. The .zip file is expected to be in the %LOCALAPPDATA%\\Temp directory.

    Args:
        cache_name (str): The name of the cache folder to look for. Defaults to "scoop_cache".
    """
    logger.info("Extract bundled Scoop cache, if available")

    appdata_temp_p = utils.resolve_path(r"%LOCALAPPDATA%\Temp")
    cache_source_folder_p = os.path.join(appdata_temp_p, cache_name)

    if not os.path.isdir(cache_source_folder_p):
        logger.warning("Cache folder not found, skipping...")

        try_log_installation_step("Info: No Scoop cache found", InfoBarIcon.INFORMATION)

        return

    # Copy all files in the cache source folder to the cache directory
    cache_dir = utils.resolve_path(r"%USERPROFILE%\scoop\cache")
    os.makedirs(cache_dir, exist_ok=True)

    for root, _dirs, files in os.walk(cache_source_folder_p):
        for file_to_copy in files:
            shutil.copy(os.path.join(root, file_to_copy), cache_dir)

    try_log_installation_step("Success: Copied Scoop cache", InfoBarIcon.SUCCESS)


def install_zsh_over_git():
    """
    Installs Zsh and Oh My Zsh and symlinks Zsh binaries over Git. Also installs Powerlevel10k theme.
    """
    logger.info("Install Zsh over Git using Symlinks")

    # Has this already been done?
    zsh_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\git\current\usr\bin\zsh.exe")

    if not os.path.isfile(zsh_p):
        symlink_script = r'''
        # Define the source and target directories
        $sourceDir = "$env:USERPROFILE\scoop\apps\zsh\current"
        $targetDir = "$env:USERPROFILE\scoop\apps\git\current"

        # Get all items in the source directory, including subdirectories
        Get-ChildItem -Path $sourceDir -Recurse | ForEach-Object {
            $sourceItem = $_
            $targetItemPath = $sourceItem.FullName.Replace($sourceDir, $targetDir)

            # Check if the source item is a directory
            if ($sourceItem.PSIsContainer) {
                # Create the directory structure in the target if not exists
                if (-not (Test-Path -Path $targetItemPath)) {
                    New-Item -ItemType Directory -Path $targetItemPath | Out-Null
                }
            } elseif ($sourceItem.Name -ne "install.json" -and $sourceItem.Name -ne "manifest.json") {
                # Ensure target directory exists for the file
                $targetItemDir = [System.IO.Path]::GetDirectoryName($targetItemPath)
                if (-not (Test-Path -Path $targetItemDir)) {
                    New-Item -ItemType Directory -Path $targetItemDir | Out-Null
                }

                # Create a symlink for the file
                New-Item -ItemType HardLink -Path $targetItemPath -Value $sourceItem.FullName | Out-Null
            }
        }'''

        # Execute the PowerShell script
        run_shell_command(powershell_command=symlink_script, failure_okay=True)

    else:
        logger.info("Zsh is already installed.")

    try_log_installation_step("Success: Installed Zsh over Git", InfoBarIcon.SUCCESS)

    oh_my_zsh_p = utils.resolve_path(r"%USERPROFILE%\.oh-my-zsh")

    if os.path.isdir(oh_my_zsh_p):
        logger.info("Oh My Zsh is already installed.")
    else:
        oh_my_zsh_cmd = rf"git clone https://github.com/ohmyzsh/ohmyzsh/ {oh_my_zsh_p}"
        run_shell_command(command=oh_my_zsh_cmd)

    try_log_installation_step("Success: Installed Oh My Zsh", InfoBarIcon.SUCCESS)

    powerlevel10k_p = utils.resolve_path(r"%USERPROFILE%\.oh-my-zsh\custom\themes\powerlevel10k")

    if os.path.isdir(powerlevel10k_p):
        logger.info("Powerlevel10k is already installed.")
    else:
        powerlevel10k_cmd = rf"git clone --depth=1 https://github.com/romkatv/powerlevel10k.git {powerlevel10k_p}"
        run_shell_command(command=powerlevel10k_cmd)

    try_log_installation_step("Success: Installed Powerlevel10k", InfoBarIcon.SUCCESS)


def set_fta(extension, program_p, arguments: list[str] = None):
    """
    Sets the file type association for a given extension to a program.

    Args:
        extension (str): The file extension to associate.
        program_p (str): The path to the program to associate the extension with.
    """
    program_p = utils.resolve_path(program_p)
    program_name = os.path.basename(program_p)

    path = f"Software\\Classes\\Applications\\{program_name}\\shell\\open\\command"
    if arguments:
        value = f'"{program_p}" {" ".join(arguments)} "%1"'
    else:
        value = f'"{program_p}" "%1"'

    winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, value)

    # Create entry for extension
    setuserfta_p = utils.resolve_path("%USERPROFILE%\\scoop\\apps\\setuserfta\\current\\setuserfta.exe")

    if not os.path.isfile(setuserfta_p):
        logger.warning("setuserfta not found, skipping...")
        return

    setuserfta_cmd = " ".join([setuserfta_p, f".{extension}", rf"Applications\{program_name}"])

    run_shell_command(command=setuserfta_cmd)


def set_file_type_associations(associations: dict[str, data.FileTypeAssociation]):
    """
    Sets file-type associations based on the configuration.
    """
    if not isinstance(associations, dict):
        logger.warning("Configuration is not dictionary, skipping...")
        return

    for category, association in associations.items():
        program_p = utils.resolve_path(association.path)
        arguments = association.arguments
        extensions = association.file_types

        if not program_p or not extensions:
            logger.warning("Path or extensions not found, skipping...")
            continue

        if not os.path.isfile(program_p):
            logger.warning("Program not found, skipping...")
            continue

        for extension in extensions:
            set_fta(extension, program_p, arguments)

        try_log_installation_step(f"Success: Created file-type associations for {category}", InfoBarIcon.SUCCESS)


def git_clone_repository(url, output_dir=None):
    """
    Clones a Git repository to the specified directory.

    Args:
        url (str): The URL of the Git repository to clone.
        output_dir (str, optional): The directory to clone the repository to.
            Defaults to None, in which case the repository is cloned to %USERPROFILE%\\repositories\\{repo_name}.
    """
    logger.info("Git: Clone repository %s", url)

    repo_name = url.split("/")[-1].replace(".git", "")

    if output_dir is None:
        output_dir = os.path.join(utils.resolve_path(r"%USERPROFILE%"), "repositories", repo_name)

    if os.path.isdir(output_dir):
        logger.info("Repository already cloned.")
        return

    os.makedirs(output_dir, exist_ok=True)

    run_shell_command(command=f"git.exe clone {url} {output_dir}", failure_okay=True)


def clone_git_repositories(repositories: List[data.GitRepository]):
    """
    Clones a list of Git repositories to the %USERPROFILE%\\repositories directory.
    """
    logger.info("Git: Clone configured repositories")

    for repository in repositories:
        repo_url = repository.id
        git_clone_repository(repo_url)

        repo_name = repo_url.split("/")[-1].replace(".git", "")

        try_log_installation_step(f"Success: Cloned Git repository {repo_name}", InfoBarIcon.SUCCESS)


def npm_install_libraries(libs: List[data.NpmPackage]):
    """
    Installs a list of NPM libraries globally.
    """
    logger.info("NPM: Install libraries")

    npm_cmd_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\nodejs\current\npm.cmd")

    if not os.path.isfile(npm_cmd_p):
        logger.warning("npm not found, skipping...")
        try_log_installation_step("Warning: No NodeJS package manager found", InfoBarIcon.WARNING)
        return

    for lib in libs:
        lib_id = lib.id
        lib_name = lib.name

        run_shell_command(command=f"{npm_cmd_p} install -g {lib_id}", failure_okay=True)

        try_log_installation_step(f"Success: Installed {lib_name} (NPM)", InfoBarIcon.SUCCESS)


def extract_bundled_zip():
    """
    Extracts a bundled .zip file to the %LOCALAPPDATA%\\Temp directory.

    The bundled .zip file is expected to be in the same directory as the script, with the name "bundled.zip".
    """
    logger.info("Extracted bundled ZIP file to Temp directory")

    appdata_temp_p = utils.resolve_path(r"%LOCALAPPDATA%\Temp")

    if cfg.bundledZipFile and os.path.isfile(cfg.bundledZipFile.value):
        bundled_zip_p = cfg.bundledZipFile.value
    else:
        zip_name = "bluekit_bundled.zip"
        bundled_zip_p = os.path.join(HERE, zip_name)

    # If it doesn't exist, oh no!
    if not os.path.isfile(bundled_zip_p):
        logger.warning("Bundled ZIP file not found, skipping...")
        try_log_installation_step("Info: No bundled .zip file found", InfoBarIcon.INFORMATION)

        return

    extract_and_place_file(bundled_zip_p, appdata_temp_p, extract=True)

    try_log_installation_step("Success: Extracted bundled .zip file", InfoBarIcon.SUCCESS)


def remove_worthless_python_exes():
    """
    Removes the worthless python.exe and python3.exe files from the WindowsApps directory, if they exist.
    """
    logger.info("Remove AppAlias Python executables")

    # Remove the entire folder at %USERPROFILE%\AppData\Local\Microsoft\WindowsApps
    run_shell_command(powershell_command='Remove-Item -Path $env:USERPROFILE\\AppData\\Local\\Microsoft\\WindowsApps -Recurse -Force', failure_okay=True)

    try_log_installation_step("Success: Removed AppAlias Python executables", InfoBarIcon.SUCCESS)


def make_bindiff_available_to_programs():
    """
    Configures BinDiff to be available to other programs like IDA Pro and Binary Ninja.
    """
    logger.info("Make BinDiff available to other programs like IDA Pro and Binary Ninja")

    bindiff_dir = utils.resolve_path(r"%USERPROFILE%\scoop\apps\bindiff\current")

    if not os.path.isdir(bindiff_dir):
        logger.warning("BinDiff not found, skipping...")

        try_log_installation_step("Warning: BinDiff not found, skipping!", InfoBarIcon.WARNING)

        return

    # Edit the bindiff.json to include the path to the BinDiff executable
    bindiff_json_p = os.path.join(bindiff_dir, "CommonAppData", "BinDiff", "bindiff.json")

    if not os.path.isfile(bindiff_json_p):
        logger.warning("BinDiff JSON not found, skipping...")
        return

    with open(bindiff_json_p, "r", encoding="utf-8") as bindiff_json_f:
        bindiff_data = json.loads(bindiff_json_f.read())

    bindiff_data["directory"] = os.path.join(bindiff_dir, ".")
    bindiff_data["ui"]["java_binary"] = os.path.join(bindiff_dir, "ProgramFiles", "BinDiff", "jre", "bin", "javaw.exe")
    bindiff_data["ida"]["directory"] = utils.resolve_path(r"%USERPROFILE%\scoop\apps\ida_pro\current")

    with open(bindiff_json_p, "w", encoding="utf-8") as bindiff_json_f:
        bindiff_json_f.write(json.dumps(bindiff_data, indent=4))

    # Copy the following folders:
    # ProgramFiles/BinDiff/Plugins/IDA Pro -> Appdata/Roaming/Hex-Rays/IDA Pro
    # ProgramFiles/BinDiff/Plugins/Binary Ninja -> Appdata/Roaming/Binary Ninja/plugins
    # CommonAppData -> Appdata/Roaming

    ida_pro_p = os.path.join(bindiff_dir, "ProgramFiles", "BinDiff", "Plugins", "IDA Pro")
    binary_ninja_p = os.path.join(bindiff_dir, "ProgramFiles", "BinDiff", "Plugins", "Binary Ninja")
    common_app_data_p = os.path.join(bindiff_dir, "CommonAppData")

    ida_pro_target_p = utils.resolve_path(r"%APPDATA%\Hex-Rays\IDA Pro\plugins")
    binary_ninja_target_p = utils.resolve_path(r"%APPDATA%\Binary Ninja\plugins")
    common_app_data_target_p = utils.resolve_path(r"%APPDATA%")

    if os.path.isdir(ida_pro_p):
        shutil.copytree(ida_pro_p, ida_pro_target_p, dirs_exist_ok=True)

    if os.path.isdir(binary_ninja_p):
        shutil.copytree(binary_ninja_p, binary_ninja_target_p, dirs_exist_ok=True)

    if os.path.isdir(common_app_data_p):
        shutil.copytree(common_app_data_p, common_app_data_target_p, dirs_exist_ok=True)

    try_log_installation_step("Success: Made BinDiff available to IDA Pro and Binary Ninja", InfoBarIcon.SUCCESS)


def ida_py_switch(python_dll_path: str):
    """
    Switches the Python version used by IDA Pro to the provided version.

    This function assumes that IDA Pro is installed using Scoop.
    """
    logger.info("Execute idapyswitch to configure Python version for IDA Pro")

    python_dll_path = utils.resolve_path(python_dll_path)

    key_path = r"Software\Hex-Rays\IDA"

    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, "Python3TargetDLL", 0, winreg.REG_SZ, python_dll_path)

    except Exception as e:
        print(f"Failed to update the registry: {e}")
        traceback.print_exc()

    idapyswitch_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\ida_pro\current\idapyswitch.exe")

    try:
        with subprocess.Popen(
            [idapyswitch_p],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ) as process:
            output, error = process.communicate(input="0")

            if process.returncode == 0:
                print("idapyswitch executed successfully.")
                print(output)

            else:
                print(f"idapyswitch failed with error: {error}")

    except Exception as e:
        print(f"Failed to run idapyswitch: {e}")

    try_log_installation_step("Success: Ran IDAPySwitch", InfoBarIcon.SUCCESS)


def add_paths_to_path(paths: List[str], at_start: bool = False) -> bool:
    """
    Adds a list of paths to the PATH environment variable.

    Args:
        paths (List[str]): A list of paths to add to the PATH environment variable.

    Returns:
        bool: True if any paths were added, False otherwise.
    """
    logger.info("Add paths to PATH: %s", json.dumps(paths))

    added_entries = False

    path = os.getenv("PATH")

    for p in paths:
        if p not in path:
            added_entries = True

            if at_start:
                path = f"{p};{path}"
            else:
                path += f";{p}"

    os.environ["PATH"] = path

    # Save this to the system PATH
    if added_entries:
        run_shell_command(powershell_command=f'[Environment]::SetEnvironmentVariable("PATH", "{path}", "Machine")')

    return added_entries


def scoop_install_pwsh():
    """
    Installs PowerShell Core using Scoop.
    """
    logger.info("Install PowerShell Core using Scoop")

    run_shell_command(powershell_command="scoop.cmd install pwsh", needs_refresh=True)

    try_log_installation_step("Success: Installed PowerShell 7", InfoBarIcon.SUCCESS)


def install_ida_plugins(plugins: List[data.IdaPlugin]):
    """
    Installs a list of IDA Pro plugins.
    """
    logger.info("Install IDA Pro plugins")

    possible_ida_names = ["ida_pro", "ida-free"]
    possible_plugin_paths = [f"%USERPROFILE%\\scoop\\apps\\{name}\\current\\plugins" for name in possible_ida_names]
    possible_plugin_paths = [utils.resolve_path(path) for path in possible_plugin_paths]
    possible_plugin_paths = [path for path in possible_plugin_paths if os.path.isdir(path)]

    for plugin in plugins:
        plugin_url = plugin.id
        plugin_name = plugin_url.split("/")[-1]

        for plugin_folder_p in possible_plugin_paths:
            plugin_p = os.path.join(plugin_folder_p, plugin_name)

            if os.path.isfile(plugin_p):
                logger.info("Plugin %s already installed.", plugin_name)
                try_log_installation_step(f"Info: IDA Plugin {plugin_name} already exists", InfoBarIcon.INFORMATION)
                continue

            run_shell_command(command=f"curl.exe -L -o {plugin_p} {plugin_url}")
            try_log_installation_step(f"Success: Installed IDA plugin {plugin_name}", InfoBarIcon.SUCCESS)


def convert_winreg_str_to_type(data_type_s: str) -> int:
    if data_type_s == "REG_SZ":
        data_type = winreg.REG_SZ
    elif data_type_s == "REG_DWORD":
        data_type = winreg.REG_DWORD
    elif data_type_s == "REG_BINARY":
        data_type = winreg.REG_BINARY
    elif data_type_s == "REG_EXPAND_SZ":
        data_type = winreg.REG_EXPAND_SZ
    elif data_type_s == "REG_MULTI_SZ":
        data_type = winreg.REG_MULTI_SZ
    elif data_type_s == "REG_QWORD":
        data_type = winreg.REG_QWORD
    else:
        data_type = None

    return data_type


def convert_winreg_str_to_hive(hive_s: str) -> int:
    if hive_s == "HKEY_CLASSES_ROOT":
        hive = winreg.HKEY_CLASSES_ROOT
    elif hive_s == "HKEY_CURRENT_USER":
        hive = winreg.HKEY_CURRENT_USER
    elif hive_s == "HKEY_LOCAL_MACHINE":
        hive = winreg.HKEY_LOCAL_MACHINE
    elif hive_s == "HKEY_USERS":
        hive = winreg.HKEY_USERS
    elif hive_s == "HKEY_CURRENT_CONFIG":
        hive = winreg.HKEY_CURRENT_CONFIG
    else:
        hive = None

    return hive


def make_registry_changes(registry_changes_data: dict[str, list[data.RegistryChange]]):
    """
    Makes a list of registry changes.

    Args:
        registry_changes_data (dict): A dictionary of registry changes to make.
    """
    logger.info("Make registry changes")

    for _category, registry_changes in registry_changes_data.items():
        if not isinstance(registry_changes, list):
            logger.warning("Registry changes are not a list, skipping...")
            continue

        for registry_change in registry_changes:
            key = registry_change.key
            value = registry_change.value
            registry_change_data = registry_change.data

            data_type = registry_change.type

            if isinstance(data_type, str):
                try:
                    data_type = getattr(winreg, data_type)
                except Exception:
                    logger.warning("Invalid hive, skipping...")
                    continue

            hive = registry_change.hive

            if isinstance(hive, str):
                try:
                    hive = getattr(winreg, hive)
                except Exception:
                    logger.warning("Invalid hive, skipping...")
                    continue

            if key is None or value is None or registry_change_data is None:
                logger.warning("Key, value, or data not found, skipping...")
                continue

            # Resolve the data if it's a path
            if data_type == winreg.REG_SZ:
                data_resolved = utils.resolve_path(registry_change_data)

                if data_resolved:
                    registry_change_data = data_resolved

            if data_type == winreg.REG_DWORD:
                registry_change_data = int(registry_change_data)

            try:
                winreg.CreateKey(hive, key)
                with winreg.OpenKey(hive, key, 0, winreg.KEY_WRITE) as reg_key:
                    winreg.SetValueEx(reg_key, value, 0, data_type, registry_change_data)

            except Exception as e:
                print(f"Failed to update the registry: {e}")
                traceback.print_exc()

    try_log_installation_step("Success: Made registry changes", InfoBarIcon.SUCCESS)


def install_miscellaneous_files(misc_files: dict[str, list[data.MiscFile]]):
    """
    Downloads and places miscellaneous files to the specified target directories.
    """
    logger.info("Install miscellaneous files")

    for _category, entries in misc_files.items():
        if not isinstance(entries, list):
            logger.warning("Entries are not a list, skipping...")
            continue

        for entry in entries:
            if not isinstance(entry, data.MiscFile):
                logger.warning("Entry is not a MiscFile, skipping...")
                continue

            sources = entry.sources
            target = entry.target

            if not sources or not target:
                logger.warning("Source or target not found, skipping...")
                continue

            target_folder = utils.resolve_path(target)

            if os.path.isfile(target_folder):
                # The target is supposed to be a folder, so this is a problem
                logger.warning("Target is a file, skipping...")

            os.makedirs(target_folder, exist_ok=True)

            for url in sources:
                destination = os.path.join(target_folder, os.path.basename(url))

                if " " in destination:
                    command_parts = ["curl.exe", "-L", "-o", destination, url]
                    run_shell_command(command_parts=command_parts, failure_okay=True)
                else:
                    run_shell_command(command=f"curl.exe -L -o {destination} {url}", failure_okay=True)

                # Extract the file if it's a .zip
                if destination.endswith(".zip"):
                    utils.extract_zip(destination, target_folder)

            try_log_installation_step(f"Success: Installed {entry.description} (Miscellaneous)", InfoBarIcon.SUCCESS)


def apply_registry_change(hive: int, key: str, value: str, data_type: int, data: any):  # pylint: disable=redefined-outer-name
    winreg.CreateKey(hive, key)
    with winreg.OpenKey(hive, key, 0, winreg.KEY_WRITE) as reg_key:
        winreg.SetValueEx(reg_key, value, 0, data_type, data)


def enable_windows_safer():
    hive = winreg.HKEY_LOCAL_MACHINE
    base_key = "SOFTWARE\\Policies\\Microsoft\\Windows\\Safer\\CodeIdentifiers"

    apply_registry_change(hive, base_key, "authenticodeenabled", winreg.REG_DWORD, 0)
    apply_registry_change(hive, base_key, "DefaultLevel", winreg.REG_DWORD, 0x9c40)

    executable_types_data = [
        "ADE",
        "ADP",
        "BAS",
        "CHM",
        "CRT",
        "HLP",
        "HTA",
        "HTC",
        "INF",
        "INS",
        "ISP",
        "JOB",
        "MDB",
        "MDE",
        "MSC",
        "MSI",
        "MSP",
        "MST",
        "PCD",
        "PIF",
        "PS1",
        "REG",
        "SCT",
        "SHS",
        "TMP",
        "VB",
        "WPC",
        "WSC",
    ]

    apply_registry_change(hive, base_key, "ExecutableTypes", winreg.REG_MULTI_SZ, executable_types_data)
    apply_registry_change(hive, base_key, "Levels", winreg.REG_DWORD, 0x71000)
    apply_registry_change(hive, base_key, "LogFileName", winreg.REG_SZ, "C:\\Windows\\system32\\LogFiles\\SAFER.LOG")
    apply_registry_change(hive, base_key, "PolicyScope", winreg.REG_DWORD, 0)
    apply_registry_change(hive, base_key, "TransparentEnabled", winreg.REG_DWORD, 2)

    apply_registry_change(hive, "SOFTWARE\\Microsoft\\Windows Script Host\\Settings", "UseWinSAFER", winreg.REG_SZ, "1")
    apply_registry_change(hive, "SOFTWARE\\Policies\\Microsoft\\SystemCertificates\\TrustedPublisher\\Safer", "AuthentiCodeFlags", winreg.REG_DWORD, 0x300)
    apply_registry_change(hive, "SYSTEM\\CurrentControlSet\\Control\\Srp\\GP", "RuleCount", winreg.REG_DWORD, 0)

    # Create empty keys for all the levels
    bases = [
        "SOFTWARE\\Policies\\Microsoft\\safer\\codeidentifiers",
        "SOFTWARE\\WOW6432Node\\Policies\\Microsoft\\Windows\\safer\\codeidentifiers"
    ]

    levels = [
        "0",
        "131072",
        "262144",
        "4096",
        "65536"
    ]

    keys = [
        "Hashes",
        "Paths",
        "URLZones"
    ]

    for base in bases:
        for level in levels:
            for key in keys:
                level_key = "\\".join([base, level, key])
                winreg.CreateKey(hive, level_key)


def register_windows_safer_path(malware_p: str):
    malware_p = utils.resolve_path(malware_p)
    os.makedirs(malware_p, exist_ok=True)

    hive = winreg.HKEY_LOCAL_MACHINE

    bases = [
        "SOFTWARE\\Policies\\Microsoft\\safer\\codeidentifiers",
        "SOFTWARE\\WOW6432Node\\Policies\\Microsoft\\Windows\\safer\\codeidentifiers"
    ]

    # Generate a guid
    malware_path_guid = f"{{{uuid.uuid4()}}}"

    for base in bases:
        malware_path_key = "\\".join([base, "0", "Paths", malware_path_guid])
        winreg.CreateKey(hive, malware_path_key)

        apply_registry_change(hive, malware_path_key, "Description", winreg.REG_SZ, "Malware Path")
        apply_registry_change(hive, malware_path_key, "ItemData", winreg.REG_SZ, malware_p)
        apply_registry_change(hive, malware_path_key, "LastModified", winreg.REG_BINARY, bytearray.fromhex("c014546e8df9c501"))
        apply_registry_change(hive, malware_path_key, "SaferFlags", winreg.REG_DWORD, 0)


def install_bluekit(configuration: data.Configuration, should_restart: bool = True):
    """
    Overall method for performing all of Bluekit's installations steps.
    """
    with open(configuration_out_p, "w+", encoding="utf-8") as configuration_out_f:
        configuration_out_f.write(json.dumps(configuration, default=asdict, indent=4))

    common_pre_install()
    remove_worthless_python_exes()
    extract_bundled_zip()
    extract_scoop_cache()

    # Tooling for the rest of the installation
    install_scoop()
    scoop_install_git()
    scoop_install_pwsh()

    # Registry changes early in case they are relevant during installation
    make_registry_changes(configuration.registry_changes.changes)

    scoop_add_buckets(configuration.scoop.buckets)

    # Required packages and pip packages first
    scoop_install_tooling({"Required": configuration.scoop.required}, keep_cache=cfg.scoopKeepCache.value)
    pip_install_packages(configuration.pip.required)

    # Add MSVC_BIN and SDK_BIN to path because PortableBuildTools is inexplicably unstable
    add_paths_to_path([utils.resolve_path("%MSVC_BIN%"), utils.resolve_path("%SDK_BIN%")], at_start=True)

    # Add pipx output directory to PATH
    add_paths_to_path([utils.resolve_path(r"%USERPROFILE%\.local\bin")])

    scoop_install_tooling(configuration.scoop.packages, keep_cache=cfg.scoopKeepCache.value)
    pip_install_packages(configuration.pip.packages)
    npm_install_libraries(configuration.npm.packages)
    install_ida_plugins(configuration.ida_plugins.plugins)
    set_file_type_associations(configuration.file_type_associations.associations)
    pin_apps_to_taskbar(configuration.taskbar_pins.pins)
    clone_git_repositories(configuration.git_repositories.repositories)
    install_vscode_extensions(configuration.vscode_extensions.extensions)
    install_miscellaneous_files(configuration.misc_files.files)

    # Run IDAPySwitch to ensure that IDA Pro works immediately after installation
    ida_py_switch(configuration.settings.ida_py_switch)

    # Make Bindiff available to other programs
    if cfg.makeBindiffAvailable.value:
        make_bindiff_available_to_programs()

    # Install Zsh on top of git
    if cfg.installZsh.value:
        install_zsh_over_git()

    # Fix Safer and restrict the malware path
    if cfg.saferEnabled.value:
        enable_windows_safer()

        for malware_p in cfg.malwareFolders.value:
            register_windows_safer_path(malware_p=malware_p)

    common_post_install()

    if cfg.scoopKeepCache.value:
        clean_up_disk(keep_cache=True)
    else:
        clean_up_disk()

    # Format the log files after the fact because they just KEEP having those damn doubled newlines
    for p in [log_p, errors_p]:
        if not os.path.isfile(p):
            continue

        with open(p, "r", encoding="utf-8") as f:
            content = f.read()

            while ("\r\n\r\n" in content) or ("\n\n" in content) or ("\r\r" in content):
                content = content.replace("\r\n\r\n", "\r\n").replace("\n\n", "\n").replace("\r\r", "\r")

        with open(p, "w+", encoding="utf-8") as f:
            f.write(content)

    if should_restart:
        restart()
