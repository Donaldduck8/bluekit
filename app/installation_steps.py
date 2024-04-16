
import json
import logging
import os
import shutil
import subprocess
import sys
import traceback
import winreg
from typing import List

import pythoncom
import win32com.client

import app.utils as utils

HERE = os.path.dirname(os.path.abspath(__file__))

if "_MEI" in HERE and getattr(sys, "frozen", False):
    # We are in a PyInstaller bundle, but I want the location of the PyInstaller executable
    HERE = os.path.dirname(sys.executable)

log_p = utils.resolve_path(r"%USERPROFILE%\install.log")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=log_p)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


def run_shell_command(command: str = None, powershell_command: str = None, command_parts: List[str] = None, failure_okay: bool = False) -> None:
    """
    Executes a shell command or a PowerShell command.

    Args:
        command (str, optional): The shell command to execute. Defaults to None.
        powershell_command (str, optional): The PowerShell command to execute. Defaults to None.
        command_parts (List[str], optional): The command parts to execute. Defaults to None.
        failure_okay (bool, optional): Whether failure is allowed. Defaults to False.
    Returns:
        None
    Raises:
        Exception: If the command execution fails and failure_okay is False.
    """
    try:
        if command:
            logger.info(f"Running Shell command: '{command}'")
            subprocess.run(command.split(" "), check=True)
        elif powershell_command:
            logger.info(f"Running PowerShell command: '{powershell_command}'")
            subprocess.run(["powershell", "-Command", powershell_command], check=True)
        elif command_parts:
            logger.info(f"Running Shell command: '{json.dumps(command_parts)}'")
            subprocess.run(command_parts, check=True)
    except Exception as e:
        if failure_okay:
            logger.warning(f"Failed to run command: {e}")
        else:
            logger.error(f"Failed to run command: {e}")
            raise e


def install_scoop() -> None:
    """
    Installs Scoop package manager if it is not already installed.
    """
    logger.info("Installing Scoop")

    # Check if scoop is already installed
    if shutil.which("scoop.cmd") is not None:
        logger.info("Scoop is already installed.")
        return

    install_script_p = os.path.join(HERE, "install_scoop.ps1")

    command = f"""
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Invoke-RestMethod -Uri https://get.scoop.sh -O {install_script_p}
    {install_script_p} -RunAsAdmin
    """

    run_shell_command(powershell_command=command)


def scoop_install_git() -> None:
    """
    Explicitly installs Git using Scoop package manager.

    Git is required for various operations, such as updating Scoop or adding buckets, so an explicit installation is nice-to-have.
    """
    logger.info("Scoop: Install Git")

    run_shell_command(command="scoop.cmd install git")


def scoop_add_buckets(buckets: List[str]):
    """
    Adds Scoop buckets to the package manager.

    Args:
        buckets (List[str]): A list of bucket names to add.

    Returns:
        None
    """
    logger.info("Scoop: Add buckets")

    for bucket in buckets:
        if isinstance(bucket, str):
            run_shell_command(command=f"scoop.cmd bucket add {bucket}")
        elif isinstance(bucket, tuple) or isinstance(bucket, list):
            run_shell_command(command=f"scoop.cmd bucket add {bucket[0]}")


def pip_install_packages(packages: List[str]):
    """
    Installs Python packages using pip.

    Args:
        packages (List[str]): A list of Python packages to install.

    Returns:
        None
    """
    logger.info("PIP: Install packages")

    for package in packages:
        if isinstance(package, str):
            run_shell_command(command=f"pip.exe install {package}")
        elif isinstance(package, tuple) or isinstance(package, list):
            run_shell_command(command=f"pip.exe install {package[0]}")


def install_build_tools():
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


def scoop_install_tool(tool_name: str, tool_name_pretty: str = None) -> bool:
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
            run_shell_command(command=f"scoop.cmd install {tool_name}")

        return True
    except Exception:
        traceback.print_exc()
        logger.warning(f"Failed to install {tool_name}, skipping...")
        return False


def scoop_install_tooling(tools: dict, install_context=True, install_associations=True):
    """
    Installs tools using Scoop package manager.

    Args:
        tools dict: TODO
        install_context (bool, optional): Whether to install context menu items. Defaults to True.
        install_associations (bool, optional): Whether to install file associations. Defaults to True.

    Returns:
        None
    """
    logger.info("Scoop: Install Tooling")

    # Ensure aria2 is installed first in order to make use of potential scoop cache
    subprocess.run("scoop.cmd install aria2".split(" "), check=True)
    # Turn off the aria2 warning
    subprocess.run("scoop.cmd config aria2-warning-enabled false".split(" "), check=True)

    for category, data in tools.items():
        if category == "Buckets":
            continue

        if not isinstance(data, list):
            logger.warning("Data is not list, skipping...")
            continue

        for tool in data:
            if isinstance(tool, str):
                tool_name = tool
                scoop_install_tool(tool)

            elif isinstance(tool, list) or isinstance(tool, tuple):
                tool_name = tool[0]
                scoop_install_tool(tool_name, tool[1])

            elif isinstance(tool, dict):
                if not tool.get("type") == "one_of":
                    logger.warning("Tool type is not one_of, skipping...")
                    continue

                tool_name = tool.get("main")[0]
                tool_name_pretty = tool.get("main")[1]
                if not scoop_install_tool(tool_name, tool_name_pretty):
                    tool_name = tool.get("alternative")[0]
                    tool_name_pretty = tool.get("alternative")[1]
                    scoop_install_tool(tool_name, tool_name_pretty)
            else:
                logger.warning("Tool is not string, list, tuple, or dict, skipping...")
                continue

            if install_context or install_associations:
                tool_dir = os.path.join(utils.SCOOP_DIR, "apps", tool_name, "current")

                tool_context_reg_p = os.path.join(tool_dir, "install-context.reg")
                tool_file_associations_reg_p = os.path.join(tool_dir, "install-file-associations.reg")

                if install_context and os.path.isfile(tool_context_reg_p):
                    run_shell_command(f"regedit /s {tool_context_reg_p}")

                if install_associations and os.path.isfile(tool_file_associations_reg_p):
                    run_shell_command(f"regedit /s {tool_file_associations_reg_p}")


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


def obtain_and_place_malware_analysis_configurations():
    """
    Obtains and places malware analysis configurations from a GitHub repository.

    The configurations include color schemes, extensions, and settings for various tools used in malware analysis.
    """
    logger.info("Obtain and place malware analysis configurations")

    config_path = utils.resolve_path(r"%USERPROFILE%\.config\malware-analysis-configurations")

    if os.path.isdir(config_path):
        logger.info("Configurations already exist, skipping...")
        return

    run_shell_command(command=f"git.exe clone https://github.com/Donaldduck8/malware-analysis-configurations {config_path}")

    # Basic symlinking operations
    for entry in os.listdir(config_path):
        logger.info(entry)

        entry_dir = os.path.join(config_path, entry)
        path_file_p = os.path.join(entry_dir, "__path")

        if not os.path.isfile(path_file_p):
            logger.info("No __path file found, skipping...")
            continue

        path_file_content = open(path_file_p, "r").read().strip()
        target_paths = path_file_content.split("\n")

        for target_path in target_paths:
            resolved_path = utils.resolve_path(target_path)

            if resolved_path is None:
                logger.warning("Could not resolve path, skipping...")
                continue
            else:
                logger.info("Writing to %s", resolved_path)

            os.makedirs(resolved_path, exist_ok=True)

            utils.link_files_and_folders(entry_dir, resolved_path)

        # Extra operations, like installing VS Code extensions
        if entry == "__vscode_extensions":
            vscode_cmd_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\vscode\current\bin\code.cmd")
            vscodium_cmd_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\vscodium\current\bin\codium.cmd")

            extensions_file_p = os.path.join(entry_dir, "extensions.json")

            if not os.path.isfile(extensions_file_p):
                logger.warning("Could not find extensions.json, skipping...")
                continue

            extensions_data = json.loads(open(extensions_file_p, "r").read())

            for extension in extensions_data:
                extension_id = extension["identifier"]["id"]

                if os.path.isfile(vscode_cmd_p):
                    run_shell_command(command=f"{vscode_cmd_p} --install-extension {extension_id}", failure_okay=True)

                if os.path.isfile(vscodium_cmd_p):
                    run_shell_command(command=f"{vscodium_cmd_p} --install-extension {extension_id}", failure_okay=True)


def remove_taskbar_pin(app_name):
    """
    Removes a pinned item from the taskbar.

    Args:
        app_name (str): The name of the application to remove from the taskbar.

    Returns:
        None
    """
    logger.info(f"Remove from Taskbar: '{app_name}'")

    command = "".join([
        # Get all currently pinned items
        """((New-Object -Com Shell.Application).NameSpace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}").Items() | """,

        # Filter out the item with the specified name and get its verbs
        "?{$_.Name -eq '" + app_name + "'}).Verbs() | ",

        # Filter out the verb that unpins the item and execute it
        "?{$_.Name.replace('&','') -match 'Unpin from taskbar'} | ",
        "%{$_.DoIt(); $exec = $true}"
    ])

    run_shell_command(powershell_command=command, failure_okay=True)


def remove_task_view():
    """
    Removes the Task View button from the taskbar.
    """
    logger.info("Remove the Task View button")

    path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced"
    value = 0
    name = "ShowTaskViewButton"

    winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)


def pin_to_taskbar(program_path, shortcut_path):
    """
    Pins an application to the taskbar.
    """
    logger.info(f"Pin to Taskbar: '{program_path}'")

    # PowerShell script to create a shortcut and pin it to the taskbar
    ps_script = rf'''
    function Create-Shortcut {{
        param (
            [string]$TargetPath,
            [string]$ShortcutPath
        )

        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = $TargetPath
        $Shortcut.Save()
    }}

    # Create shortcut
    Create-Shortcut -TargetPath "{program_path}" -ShortcutPath "{shortcut_path}"

    # Pin shortcut to the taskbar
    $shell = New-Object -ComObject Shell.Application
    $taskbarPath = [System.IO.Path]::Combine([Environment]::GetFolderPath('ApplicationData'), 'Microsoft\Internet Explorer\Quick Launch\User Pinned\TaskBar')
    $shell.Namespace($taskbarPath).Self.InvokeVerb('pindirectory', "{shortcut_path}")
    '''

    # Execute the PowerShell script
    run_shell_command(powershell_command=ps_script, failure_okay=True)


def pin_apps_to_taskbar(apps: List[str]):
    """
    Pins applications to the taskbar using a startLayout.xml file.

    The startLayout.xml file is created with the specified apps and takes effect on the next login.
    """
    app_paths = []

    for app in apps:
        if isinstance(app, str):
            app_paths.append(app)
        elif isinstance(app, list) or isinstance(app, tuple):
            app_paths.append(app[0])

    logger.info(f"Pin Apps to Taskbar: '{app_paths}'")

    xml_content = utils.create_start_layout_xml(apps=app_paths)

    # Write layout .XML file
    xml_p = utils.resolve_path(r"%USERPROFILE%\Documents\startLayout.xml")

    with open(xml_p, "w+", encoding="UTF-8") as xml_f:
        xml_f.write(xml_content)

    ps_script = r'''Write-Host "Installing NuGet"
Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force

Write-host "Trusting PS Gallery"
Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted

Write-Host "Installing PolicyFileEditor V3"
Install-Module -Name PolicyFileEditor -RequiredVersion 3.0.0 -Scope CurrentUser

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

Import-Module PolicyFileEditor

$UserDir = "$env:windir\system32\GroupPolicy\User\registry.pol"

Set-PolicyFileEntry -Path $UserDir -Key "Software\Policies\Microsoft\Windows\Explorer" -ValueName "StartLayoutFile" -Type String -Data "$env:userprofile\Documents\startLayout.xml"

# Set the path to the registry key
$registryPath = "HKCU:\Software\Policies\Microsoft\Windows\Explorer"

# The name of the DWORD value to modify/create
$valueName = "LockedStartLayout"

# The value to set the DWORD to
$valueData = 1

# Check if the registry path exists, create it if it doesn't
if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

# Set the value of the DWORD key, creating it if it doesn't exist
Set-ItemProperty -Path $registryPath -Name $valueName -Value $valueData -Type DWORD

# Set the path to the registry key
$registryPath = "HKCU:Software\Microsoft\Windows\CurrentVersion\Group Policy Objects\{7810E935-4876-4362-BF9C-D1EA60BCBB24}User\Software\Policies\Microsoft\Windows\Explorer"

# The name of the DWORD value to modify/create
$valueName = "LockedStartLayout"

# The value to set the DWORD to
$valueData = 1

# Check if the registry path exists, create it if it doesn't
if (-not (Test-Path $registryPath)) {
    New-Item -Path $registryPath -Force
}

# Set the value of the DWORD key, creating it if it doesn't exist
Set-ItemProperty -Path $registryPath -Name $valueName -Value $valueData -Type DWORD

gpupdate.exe /force'''

    # Execute the PowerShell script
    subprocess.run(['powershell', '-Command', ps_script], check=True)


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
    subprocess.run(['powershell', '-Command', ps_script], check=True)


def hide_desktop_icons():
    """
    Hides desktop icons by modifying the registry.
    """
    logger.info("Hide Desktop icons")

    path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced"
    value = 1
    name = "HideIcons"

    winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)


def hide_onedrive_pin():
    """
    Hides the OneDrive icon from the File Explorer navigation pane.
    """
    logger.info("Hide OneDrive pin")

    ps_script = r'''New-PSDrive -Name "HKCR" -PSProvider Registry -Root "HKEY_CLASSES_ROOT"

# Registry path without root
$regPath = "HKCR:\CLSID\{018D5C66-4533-4307-9B53-224DE2ED1FE6}"

# propertyName of the value to change
$propertyName = "System.IsPinnedToNameSpaceTree"

# Setting the property value to 1 to hide desktop icons
$propertyValue = 0

# Checking if the property already exists
if (Get-ItemProperty -Path $regPath -Name $propertyName -ErrorAction SilentlyContinue) {
    # Property exists, updating its value
    Set-ItemProperty -Path $regPath -Name $propertyName -Value $propertyValue
} else {
    # Property doesn't exist, creating and setting its value
    New-ItemProperty -Path $regPath -Name $propertyName -Value $propertyValue -PropertyType DWORD
}'''

    # Execute the PowerShell script
    subprocess.run(['powershell', '-Command', ps_script], check=True)


def common_post_install():
    """
    Executes common post-installation tasks.
    """
    logger.info("Common post-installation steps")

    functions = [
        prepare_quick_access,
        remove_taskbar_pin("Microsoft Store"),
        remove_taskbar_pin("Microsoft Edge"),
        remove_task_view,
        hide_desktop_icons,
        make_vm_stay_awake,
        make_scoop_buckets_safe,
    ]

    for function in functions:
        try:
            function()
        except Exception:
            traceback.print_exc()
            pass


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
    with open(application_json_p, "r") as application_json_f:
        scoop_data = json.loads(application_json_f.read())

    # Point the scoop URL at the extracted ZIP file
    scoop_data["url"] = "file://" + application_zip_p.replace("\\", "/")

    # Write the JSON file back
    with open(application_json_p, "w") as application_json_f:
        application_json_f.write(json.dumps(scoop_data, indent=4))

    # Disable aria2 for the installation to allow file:// URLs
    subprocess.run("scoop.cmd config aria2-enabled false".split(" "), check=True)

    # Install the application
    subprocess.run(f"scoop.cmd install {application_json_p}".split(" "), check=True)

    # Re-enable aria2
    subprocess.run("scoop.cmd config aria2-enabled true".split(" "), check=True)

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


def clean_up_disk():
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
            for f in files:
                try:
                    os.unlink(os.path.join(root, f))
                except Exception:
                    pass
            for d in dirs:
                try:
                    shutil.rmtree(os.path.join(root, d))
                except Exception:
                    pass

    cache_dir = utils.resolve_path(r"%USERPROFILE%\scoop\cache")
    temp_dir = utils.resolve_path(r"%LOCALAPPDATA%\Temp")
    software_distribution_dir = utils.resolve_path(r"C:\Windows\SoftwareDistribution\Download")
    windows_temp_dir = utils.resolve_path(r"C:\Windows\Temp")
    onedrive_dir = utils.resolve_path(r"%LOCALAPPDATA%\Microsoft\OneDrive")
    random_cache_dir = utils.resolve_path(r"C:\Windows\ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache")
    package_cache_dir = r"C:\ProgramData\Package Cache"

    folders = [
        cache_dir,
        temp_dir,
        software_distribution_dir,
        windows_temp_dir,
        onedrive_dir,
        random_cache_dir,
        package_cache_dir
    ]

    for folder in folders:
        delete_everything_recursively_in_directory(folder)

    # subprocess.run("Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase".split(" "), check=True)


def extract_scoop_cache(cache_name: str = "scoop_cache"):
    """
    Extracts a .zip file to the Scoop cache directory. The .zip file is expected to be in the %LOCALAPPDATA%\\Temp directory.

    Args:
        cache_name (str): The name of the cache ZIP file to extract. Defaults to "scoop_cache".
    """
    logger.info(f"Extract bundled Scoop cache, if available")

    appdata_temp_p = utils.resolve_path(r"%LOCALAPPDATA%\Temp")
    cache_zip_p = os.path.join(appdata_temp_p, f"{cache_name}.zip")

    if not os.path.isfile(cache_zip_p):
        logger.warning("Cache ZIP file not found, skipping...")
        return

    # Extract the ZIP file to the cache directory
    cache_dir = utils.resolve_path(r"%USERPROFILE%\scoop\cache")
    os.makedirs(cache_dir, exist_ok=True)

    utils.extract_zip(cache_zip_p, cache_dir)


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
            $sourceItem.Name | Out-Host;
            $targetItemPath = $sourceItem.FullName.Replace($sourceDir, $targetDir)

            # Check if the source item is a directory
            if ($sourceItem.PSIsContainer) {
                # Create the directory structure in the target if not exists
                if (-not (Test-Path -Path $targetItemPath)) {
                    New-Item -ItemType Directory -Path $targetItemPath | Out-Null
                }
            } else {
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
        subprocess.run(['powershell', '-Command', symlink_script], check=True)

    else:
        logger.info("Zsh is already installed.")

    oh_my_zsh_p = utils.resolve_path(r"%USERPROFILE%\.oh-my-zsh")

    if os.path.isdir(oh_my_zsh_p):
        logger.info("Oh My Zsh is already installed.")
    else:
        oh_my_zsh_cmd = rf"git clone https://github.com/ohmyzsh/ohmyzsh/ {oh_my_zsh_p}"
        subprocess.run(oh_my_zsh_cmd.split(" "), check=True)

    powerlevel10k_p = utils.resolve_path(r"%USERPROFILE%\.oh-my-zsh\custom\themes\powerlevel10k")

    if os.path.isdir(powerlevel10k_p):
        logger.info("Powerlevel10k is already installed.")
    else:
        powerlevel10k_cmd = rf"git clone --depth=1 https://github.com/romkatv/powerlevel10k.git {powerlevel10k_p}"
        subprocess.run(powerlevel10k_cmd.split(" "), check=True)


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

    subprocess.run([setuserfta_p, f".{extension}", rf"Applications\{program_name}"], check=True)


def set_file_type_associations(configuration: dict):
    if not configuration:
        return

    if not isinstance(configuration, dict):
        logger.warning("Configuration is not dictionary, skipping...")
        return

    for _category, data in configuration.items():
        if not isinstance(data, dict):
            logger.warning("Data is not dictionary, skipping...")
            continue

        program_p = utils.resolve_path(data.get("path"))
        arguments = data.get("arguments")
        extensions = data.get("file_types")

        if not program_p or not extensions:
            logger.warning("Path or extensions not found, skipping...")
            continue

        if not os.path.isfile(program_p):
            logger.warning("Program not found, skipping...")
            continue

        for extension in extensions:
            set_fta(extension, program_p, arguments)


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

    run_shell_command(command=f"git.exe clone {url} {output_dir}")


def clone_git_repositories(repositories: List[str]):
    """
    Clones a list of Git repositories to the %USERPROFILE%\\repositories directory.

    Args:
        repositories (List[str]): A list of Git repository URLs to clone.
    """
    logger.info("Git: Clone configured repositories")

    for repository in repositories:
        if isinstance(repository, str):
            git_clone_repository(repository)
        elif isinstance(repository, list) or isinstance(repository, tuple):
            git_clone_repository(repository[0])


def npm_install_libraries(libs: List[str]):
    """
    Installs a list of NPM libraries globally.

    Args:
        libs (List[str], optional): A list of NPM libraries to install.
    """
    logger.info("NPM: Install libraries")

    npm_cmd_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\nodejs\current\npm.cmd")

    if not os.path.isfile(npm_cmd_p):
        logger.warning("npm not found, skipping...")
        return

    for lib in libs:
        if isinstance(lib, str):
            run_shell_command(f"{npm_cmd_p} install -g {lib}")

        elif isinstance(lib, list) or isinstance(lib, tuple):
            run_shell_command(f"{npm_cmd_p} install -g {lib[0]}")


def extract_bundled_zip():
    """
    Extracts a bundled .zip file to the %LOCALAPPDATA%\\Temp directory.

    The bundled .zip file is expected to be in the same directory as the script, with the name "bundled.zip".
    """
    logger.info("Extracted bundled ZIP file to Temp directory")

    appdata_temp_p = utils.resolve_path(r"%LOCALAPPDATA%\Temp")

    # If frozen
    if getattr(sys, "frozen", False):
        bundled_zip_p = os.path.join(sys._MEIPASS, "files", "bundled.zip")

        if not os.path.isfile(bundled_zip_p):
            bundled_zip_p = os.path.join(HERE, "bundled.zip")
    else:
        bundled_zip_p = os.path.join(HERE, "bundled.zip")

    print("Looking", bundled_zip_p)

    # If it doesn't exist, oh no!
    if not os.path.isfile(bundled_zip_p):
        logger.warning("Bundled ZIP file not found, skipping...")
        return

    extract_and_place_file(bundled_zip_p, appdata_temp_p, extract=True)


def add_npcap_installer_to_runonce():
    """
    Adds the Npcap installer to the RunOnce registry key to run at the next login.
    """
    logger.info("Add Npcap installer to RunOnce")

    npcap_installer_p = utils.resolve_path(r"%USERPROFILE%\scoop\apps\wireshark\current\npcap-installer.exe")

    if not os.path.isfile(npcap_installer_p):
        logger.warning("Npcap installer not found, skipping...")
        return

    command = " ".join([
        "Set-ItemProperty",
        "-Path HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
        "-Name 'NpcapInstaller'",
        "-Type 'String'",
        f"-Value '{npcap_installer_p}'"
    ])

    run_shell_command(powershell_command=command)


def remove_worthless_python_exes():
    """
    Removes the worthless python.exe and python3.exe files from the WindowsApps directory, if they exist.
    """
    logger.info("Remove worthless Python executables")

    # Check if the worthless files exist

    # Just delete the entire fucking folder wtf

    python_exe_p = utils.resolve_path(r"%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe")
    python3_exe_p = utils.resolve_path(r"%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe")

    if os.path.isfile(python_exe_p):
        run_shell_command(powershell_command=f"Remove-Item {python_exe_p}")

    if os.path.isfile(python3_exe_p):
        run_shell_command(powershell_command=f"Remove-Item {python3_exe_p}")


def make_bindiff_available_to_programs():
    """
    Configures BinDiff to be available to other programs like IDA Pro and Binary Ninja.
    """
    logger.info("Make BinDiff available to other programs like IDA Pro and Binary Ninja")

    bindiff_dir = utils.resolve_path(r"%USERPROFILE%\scoop\apps\bindiff\current")

    if not os.path.isdir(bindiff_dir):
        logger.warning("BinDiff not found, skipping...")
        return

    # Edit the bindiff.json to include the path to the BinDiff executable
    bindiff_json_p = os.path.join(bindiff_dir, "CommonAppData", "BinDiff", "bindiff.json")

    if not os.path.isfile(bindiff_json_p):
        logger.warning("BinDiff JSON not found, skipping...")
        return

    bindiff_data = json.loads(open(bindiff_json_p, "r").read())

    bindiff_data["directory"] = os.path.join(bindiff_dir, ".")
    bindiff_data["ui"]["java_binary"] = os.path.join(bindiff_dir, "ProgramFiles", "BinDiff", "jre", "bin", "javaw.exe")
    bindiff_data["ida"]["directory"] = utils.resolve_path(r"%USERPROFILE%\scoop\apps\ida_pro\current")

    with open(bindiff_json_p, "w") as bindiff_json_f:
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


def install_net_3_5():
    """
    Installs .NET Framework 3.5 using DISM.
    """
    logger.info("Install .NET Framework 3.5")

    run_shell_command(powershell_command="Dism /online /Enable-Feature /FeatureName:NetFx3", failure_okay=True)


def enable_dark_mode():
    """
    Enables dark mode using the registry.
    """
    logger.info("Enable Dark Mode")

    path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
    value = 0
    name = "AppsUseLightTheme"

    winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)


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
        process = subprocess.Popen(
            [idapyswitch_p],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        output, error = process.communicate(input="0")

        if process.returncode == 0:
            print("idapyswitch executed successfully.")
            print(output)

        else:
            print(f"idapyswitch failed with error: {error}")
    except Exception as e:
        print(f"Failed to run idapyswitch: {e}")


def add_paths_to_path(paths: List[str]) -> bool:
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
            path += f";{p}"

    os.environ["PATH"] = path

    # Save this to the system PATH
    if added_entries:
        run_shell_command(powershell_command=f'[Environment]::SetEnvironmentVariable("PATH", "{path}", "User")')

    return added_entries


def scoop_install_pwsh():
    """
    Installs PowerShell Core using Scoop.
    """
    logger.info("Install PowerShell Core using Scoop")

    run_shell_command(powershell_command="scoop.cmd install pwsh")


def install_ida_plugins(plugins: List[str]):
    """
    Installs a list of IDA Pro plugins.

    Args:
        plugins (List[str]): A list of python files to place into the plugins folder
    """
    logger.info("Install IDA Pro plugins")

    possible_ida_names = ["ida_pro", "ida-free"]
    possible_plugin_paths = [fr"%USERPROFILE%\scoop\apps\{name}\current\plugins" for name in possible_ida_names]
    possible_plugin_paths = [utils.resolve_path(path) for path in possible_plugin_paths]
    possible_plugin_paths = [path for path in possible_plugin_paths if os.path.isdir(path)]

    for plugin in plugins:
        if isinstance(plugin, str):
            plugin_url = plugin
        elif isinstance(plugin, list) or isinstance(plugin, tuple):
            plugin_url = plugin[0]
        else:
            logger.warning("Invalid plugin format, skipping...")
            continue

        plugin_name = plugin_url.split("/")[-1]

        for plugin_folder_p in possible_plugin_paths:
            plugin_p = os.path.join(plugin_folder_p, plugin_name)

            if os.path.isfile(plugin_p):
                logger.info("Plugin %s already installed.", plugin_name)
                continue

            run_shell_command(command=f"curl.exe -L -o {plugin_p} {plugin_url}")
