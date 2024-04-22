import json

from natsort import natsorted, ns

from app import utils

version = "1.0.0"

required_paths = [
    utils.resolve_path("%USERPROFILE%\\scoop\\shims"),
    utils.resolve_path("%USERPROFILE%\\scoop\\apps\\python311\\current"),
    utils.resolve_path("%USERPROFILE%\\scoop\\apps\\python311\\current\\Scripts"),
    utils.resolve_path("%USERPROFILE%\\scoop\\apps\\git\\current\\usr\\bin"),
    utils.resolve_path("%USERPROFILE%\\scoop\\apps\\nodejs\\current")
]

default_configuration = {
    "scoop": {
        "Buckets": [
            ("extras", "Extras", "Extra software that doesn't fit in the main bucket."),
            ("versions", "Versions", "Older versions of software."),
            ("nerd-fonts", "Nerd Fonts", "Patched fonts with a high number of glyphs."),
            ("java", "Java", "Java Development Kit and Java Runtime Environment."),
            ("malware-analysis-bucket https://github.com/Donaldduck8/malware-analysis-bucket", "Malware Analysis Bucket", "Tools for analyzing malware."),
        ],

        "Required": [
            ("git", "Git", "A distributed version control system."),
            ("pwsh", "PowerShell", "A task automation and configuration management framework."),
            ("python27", "Python 2.7", "The newest Python 2.x version available, required for Java bytecode editing."),
            ("python311", "Python 3.11", "The newest Python version currently compatible with IDA Pro.")
        ],

        "Basics": [
            # Basics
            ("FiraCode-NF-Mono", "Fira Code (Mono)", "A monospaced font with programming ligatures."),
            ("chromium", "Chromium", "A web browser that is the basis for Google Chrome."),
            ("sublime-text", "Sublime Text", "A sophisticated text editor for code, markup, and prose."),
            ("7zip", "7-Zip", "A file archiver with a high compression ratio."),
            ("vscode", "Visual Studio Code", "A code editor redefined and optimized for building and debugging modern web and cloud applications."),
        ],

        "Miscellaneous": [
            ("malware-analysis-bucket/glazewm_extra", "Glaze Window Manager", "A tiling window manager for Windows."),
            ("setuserfta", "SetUserFTA", "A tool to change the default program associated with a file type."),
            ("upx", "UPX", "A free, portable, extendable, high-performance executable packer for several executable formats."),
            ("openssl-light", "OpenSSL (Light)", "A robust, commercial-grade, and full-featured toolkit for the Transport Layer Security (TLS) and Secure Sockets Layer (SSL) protocols."),
            ("malware-analysis-bucket/onenoteanalyzer", "OneNote Analyzer", "A tool for analyzing OneNote files."),
            ("malware-analysis-bucket/pycdc", "Decompyle++", "A C++ python bytecode disassembler and decompiler."),
            ("meld", "Meld", "A visual diff and merge tool., useful for bloated script files."),
        ],

        "Shell": [
            ("windows-terminal", "Windows Terminal", "A modern terminal application for users of command-line tools and shells."),
            ("yazi", "Yazi", "A modern terminal file manager with outstanding performance."),
            ("hexyl", "Hexyl", "A simple hex viewer for the terminal."),
            ("rhash", "RHash", "A utility for computing and verifying hash sums of files."),
            ("fzf", "FZF", "A command-line fuzzy finder."),
            ("ripgrep", "Ripgrep", "A line-oriented search tool that recursively searches your current directory for a regex pattern."),
            ("zoxide", "Zoxide", "A smarter cd command."),
            ("sudo", "Sudo", "A program for providing privileged access to commands."),
            ("malware-analysis-bucket/zsh", "Zsh", "A shell designed for interactive use."),
            ("ouch", "Ouch", "A library for painless compression and decompression for your terminal."),
        ],

        # Triage
        "Triage": [
            ("die", "Detect It Easy", "A program for determining types of files."),
            ("malware-analysis-bucket/cyberchef", "Cyberchef", "A web app for analyzing and decoding data."),
            ("malware-analysis-bucket/malcat", "MalCat", "A tool centered around static malware and binary analysis."),
            ("010editor", "010 Editor", "A professional text/hex editor designed to edit any file."),
        ],

        # PE (Static)
        "PE (Static)": [
            ("yara", "YARA", "A tool aimed at helping malware researchers to identify and classify malware samples."),
            {
                "type": "one_of",
                "main": ("ida_pro.json", "IDA Pro", "A disassembler and debugger for analyzing binary files."),
                "alternative": ("ida-free", "IDA Free", "A free version of IDA Pro.")
            },
            {
                "type": "one_of",
                "main": ("binary_ninja.json", "Binary Ninja", "A reverse engineering platform."),
                "alternative": ("binary_ninja_free", "Binary Ninja Free", "A free version of Binary Ninja."),
            },
            ("ghidra", "Ghidra", "A software reverse engineering (SRE) framework."),
            ("cutter", "Cutter", "A reverse engineering platform powered by rizin/radare2 and Ghidra's decompiler."),
            ("malware-analysis-bucket/floss", "FLOSS", "A tool designed to automatically deobfuscate strings from malware samples."),
            ("malware-analysis-bucket/cffexplorer", "CFF Explorer", "A PE editor."),
            ("innoextract", "Inno Setup Extractor", "A tool for extracting Inno Setup installers."),
            ("uniextract2", "Universal Extractor 2", "A tool for extracting files from any type of archive."),
            ("malware-analysis-bucket/bindiff", "BinDiff", "A tool for comparing binary files."),
        ],

        # PE (Dynamic)
        "PE (Dynamic)": [
            ("x64dbg", "x64dbg", "An open-source x64/x32 debugger for Windows."),
            ("malware-analysis-bucket/x64dbg_plugin_manager", "x64dbg Plugin Manager", "A tool to manage and automatically install x64dbg plugins."),
            ("windbg", "WinDbg", "A multipurpose x64/x32 debugger capable of handling context switching."),
            ("pe-sieve", "PE-sieve", "a tool that helps to detect and collect malware running on the system."),
            ("wireshark", "Wireshark", "A network protocol analyzer."),
            ("hollows-hunter", "Hollows Hunter", "A tool to detect code injection techniques."),
            ("sysinternals", "Sysinternals Suite", "A suite of utilities to manage, diagnose, troubleshoot, and monitor Windows."),
            ("systeminformer-nightly", "System Informer", "A tool to gather information about your system."),
            ("malware-analysis-bucket/pe_unmapper", "PE Unmapper", "A tool to unmap dumped PE files."),
            ("malware-analysis-bucket/apimonitor", "API Monitor", "A tool to monitor and control Windows API calls made by applications."),
            ("malware-analysis-bucket/pd32", "Process Dump (x86)", "A tool to dump processes."),
            ("malware-analysis-bucket/pd64", "Process Dump (x64)", "A tool to dump processes."),
            ("malware-analysis-bucket/xntsv64", "XNTSV64", "A tool to inspect process and thread structures of running programs."),
            ("malware-analysis-bucket/regshot", "Regshot", "A tool to compare registry snapshots."),
            ("malware-analysis-bucket/mal_unpack32", "Mal_Unpack32", "A tool to unpack malware."),
            ("malware-analysis-bucket/mal_unpack64", "Mal_Unpack64", "A tool to unpack malware."),
            ("malware-analysis-bucket/novmp", "NoVMP", "A tool to unpack malware."),
            ("malware-analysis-bucket/xvolkolak", "XVolKolak", "A tool to unpack malware."),
            ("malware-analysis-bucket/fermion", "Fermion", "An electron wrapper for Frida & Monaco"),
        ],

        # Themida (Dynamic)
        "Themida (Dynamic)": [
            ("malware-analysis-bucket/magicmida", "MagicMida", "A tool designed to unpack some 32-bit Themida-protected applications."),
            ("malware-analysis-bucket/unlicense_64", "Unlicense (x64)", "A tool to unpack Themida-protected applications."),
            ("malware-analysis-bucket/unlicense_32", "Unlicense (x86)", "A tool to unpack Themida-protected applications."),
        ],

        # Shellcode (Static)
        "Shellcode (Static)": [
            ("malware-analysis-bucket/scdbg", "SCDbg", "A shellcode emulation tool to extract Windows API calls."),
        ],

        # Shellcode (Dynamic)
        "Shellcode (Dynamic)": [
            ("malware-analysis-bucket/blobrunner32", "BlobRunner (x86)", "A bootstrap program to execute shellcode within a debugger."),
            ("malware-analysis-bucket/blobrunner64", "BlobRunner (x64)", "A bootstrap program to execute shellcode within a debugger."),
        ],

        # Golang (Static)
        "Golang (Static)": [
            ("malware-analysis-bucket/goresym", "GoResym", "A Golang symbol parser that extracts program metadata, function metadata, filename and line number metadata, and embedded structures and types."),
            ("malware-analysis-bucket/redress", "Redress", "A tool for analyzing stripped Go binaries compiled with the Go compiler."),
        ],

        # Golang (Dynamic)
        "Golang (Dynamic)": [
            ("malware-analysis-bucket/gftrace32", "GFTrace (x86)", "A command line Windows API tracing tool for Golang binaries."),
            ("malware-analysis-bucket/gftrace64", "GFTrace (x64)", "A command line Windows API tracing tool for Golang binaries."),
        ],

        # .NET (Dependencies)
        ".NET (Dependencies)": [
            ("windowsdesktop-runtime-6.0", ".NET 6.0 Runtime", "Required for ILSpy"),  # ILSpy
            ("windowsdesktop-runtime-5.0_64", ".NET 5.0 (x64) Runtime", "Required for GarbageMan"),  # GarbageMan
            ("windowsdesktop-runtime-5.0_32", ".NET 5.0 (x86) Runtime", "Required for GarbageMan"),
            ("malware-analysis-bucket/dotnet7-sdk_32", ".NET 7.0 (x86) SDK", "Required for LINQPad"),  # Linqpad
            ("malware-analysis-bucket/dotnet7-sdk_64", ".NET 7.0 (x64) SDK", "Required for LINQPad"),
        ],

        # .NET (Static)
        ".NET (Static)": [
            ("ilspy", "ILSpy", "A .NET assembly browser and decompiler."),
            ("malware-analysis-bucket/dnspyex64", "dnSpyEx64", "A .NET debugger and assembly editor."),
            ("malware-analysis-bucket/dnspyex32", "dnSpyEx32", "A .NET debugger and assembly editor."),
            ("malware-analysis-bucket/de4dot-net45", "de4dot .NET 4.5", "A .NET deobfuscator and unpacker."),
            ("malware-analysis-bucket/netreactorslayer", "NetReactor Slayer", "A tool to deobfuscate .NET Reactor-protected applications."),
        ],

        # .NET (Dynamic)
        ".NET (Dynamic)": [
            ("codetrack", "CodeTrack", "A tool to monitor and analyze .NET application performance."),
            {
                "type": "one_of",
                "main": ("linqpad.json", "LINQPad", "A tool to easily write C# scripts to interact with .NET malware samples."),
                "alternative": ("linqpad", "LINQPad (Free)", "A tool to easily write C# scripts to interact with .NET malware samples."),
            },
            ("malware-analysis-bucket/extreme_dumper", "Extreme Dumper", "A tool to dump .NET assemblies from running .NET applications by hooking Assembly-related functions."),
            ("malware-analysis-bucket/dotdumper", "DotDumper", "An automatic unpacker and logger for DotNet Framework targeting files."),
            ("malware-analysis-bucket/rundotnetdll", "RunDotNetDll", "A bootstrap program to execute non-executable .NET assemblies within a debugger."),
            ("malware-analysis-bucket/psnotify-np", "PSNotify (non-portable) ", "A hooking engine required for GarbageMan."),
            ("malware-analysis-bucket/garbageman", "GarbageMan", "A set of tools for analyzing .NET binaries through heap analysis."),
            ("malware-analysis-bucket/sharpdllloader", "SharpDllLoader", "A bootstrap program to execute non-executable .NET assemblies within a debugger."),
        ],

        # PowerShell (Dynamic)
        "PowerShell (Dynamic)": [
            ("malware-analysis-bucket/powerdecode", "PowerDecode", "A tool to automatically deobfuscate some PowerShell scripts."),
        ],

        # JavaScript (Dynamic)
        "JavaScript (Dynamic)": [
            ("nodejs", "Node.js", "A JavaScript runtime built on Chrome's V8 JavaScript engine."),
        ],

        # JAVA (Dependencies)
        "JAVA (Dependencies)": [
            ("temurin17-jdk", "Temurin JDK 17", "A free and open-source implementation of the Java Platform, Standard Edition."),
        ],

        # JAVA (Static)
        "JAVA (Static)": [
            ("malware-analysis-bucket/recaf3", "Recaf 3.0.0-SNAPSHOT", "A snapshot of the current state of development of Recaf 3, which is a modern Java bytecode viewer and decompiler."),
            ("malware-analysis-bucket/recaf4", "Recaf 4.0.0-SNAPSHOT", "A snapshot of the current state of development of Recaf 4, which is a modern Java bytecode viewer and decompiler."),
            ("malware-analysis-bucket/java-disassembler", "Java Disassembler", "A tool to disassemble Java class files."),
        ],

        # JAVA (Dynamic)
        "JAVA (Dynamic)": [
            ("bytecode-viewer", "Bytecode Viewer", "A Java 8 Jar & Android APK Reverse Engineering Suite (Decompiler, Editor, Debugger & More)."),
        ],

        # Android (Static)
        "Android (Static)": [
            ("jadx", "Jadx", "A lightweight and easy-to-use decompiler for Android applications."),
            ("apktool", "Apktool", "A tool for reverse engineering Android APK files."),
        ],

        # OLE / Microsoft Office (Static)
        "OLE / Microsoft Office (Static)": [
            ("malware-analysis-bucket/didier_stevens_suite", "Didier Stevens Suite", "A collection of tools to process Microsoft Office-adjacent files."),
            ("oleviewdotnet", "OLEViewDotNet", "A tool to view all OLE class IDs present on the system."),
        ],

        # MSI (Static)
        "MSI (Static)": [
            ("malware-analysis-bucket/lessmsi", "LessMSI", "A tool to view and extract the contents of an MSI file."),
        ],

        # Rust (Static)
        # "rust",  # Relies on Visual C++ build tools
        # "rustup",  # Relies on Visual C++ build tools

        # AutoIt (Static)
        "AutoIt (Static)": [
            ("autoit-script-editor", "AutoIt Script Editor", "A script editor for AutoIt3."),
        ],

        # AutoIt (Dynamic)
        "AutoIt (Dynamic)": [
            ("autoit", "AutoIt", "A freeware automation language for Microsoft Windows."),
        ],

        # Visual Basic (Dynamic)
        "Visual Basic (Dynamic)": [
            ("malware-analysis-bucket/vbsedit", "VbsEdit", "A tool to edit and debug VBScript files."),
        ],

        # Batch scripts (Dynamic)
        "Batch scripts (Dynamic)": [
            ("malware-analysis-bucket/cmdebug", "CMDebug", "A tool to edit and debug batch files."),
        ],

        # Delphi (Static)
        "Delphi (Static)": [
            ("malware-analysis-bucket/interactive_delphi_reconstructor", "Interactive Delphi Reconstructor", "A tool to reconstruct Delphi executables."),
            ("malware-analysis-bucket/delphi_hand_rake", "Delphi Hand Rake", "A tool to utilize IDR's reconstruction results within Ghidra."),
        ],
    },

    "pip": [
        # Binref
        ("binary-refinery[all]", "Binary Refinery", "A collection of tools for reverse engineering, binary analysis and pipeline creation."),

        # Dumpulator
        ("dumpulator", "Dumpulator", "An easy-to-use library for emulating code in minidump files"),
        ("skrapa[yara]", "Skrapa", "A tool to perform YARA matches against the memory of running processes."),

        # IDA Pro
        ("envi", "Envi", "A minimal environment variables reader, required for IDAPython."),
        ("sip", "SIP", "A tool to generate Python bindings for C and C++ libraries, required for IDAPython."),
        ("PyQt5", "PyQt5", "A set of Python bindings for the Qt application framework, required for IDAPython."),

        ("construct", "Construct", "A powerful declarative parser (and builder) for binary data."),
        ("capstone", "Capstone", "A disassembly framework specialized for binary analysis."),
        ("dncil", "dnCIL", "A library that enables parsing of .NET assemblies."),
        ("dnfile", "dnFile", "A library that enables parsing of .NET assemblies."),
        ("yara-python", "yara-python", "A Python interface for YARA."),

        ("requests", "Requests", "A simple, yet elegant HTTP library."),
        ("mkyara", "mkyara", "A tool to generate YARA rules from malware samples."),

        ("unicorn", "Unicorn", "A lightweight, multi-platform, multi-architecture CPU emulator framework."),
        ("olefile", "olefile", "A Python package to parse, read, and write Microsoft OLE2 files."),
        ("oletools[full]", "oletools", "A set of tools to analyze Microsoft OLE2 files."),
        ("git+https://github.com/N0fix/rustbinsign.git", "RustBinSign", "A tool to generate FLIRT / SIGKIT signatures from Rust binaries."),

        # Donut Shellcode
        ("git+https://github.com/volexity/chaskey-lts.git", "chaskey-lts", "A Python implementation of the Chaskey-LTS block cipher."),
        ("git+https://github.com/volexity/donut-decryptor.git", "donut-decryptor", "A tool to decrypt Donut shellcode."),

        # D810
        ("z3-solver", "z3-solver", "A theorem prover from Microsoft Research."),

        # Python
        ("uncompyle6", "uncompyle6", "A Python bytecode decompiler."),
        ("decompyle3", "decompyle3", "A Python bytecode decompiler."),

        # PowerShell (Static)
        ("git+https://github.com/Donaldduck8/deobshell.git@pip-installable", "deobshell", "A tool to statically deobfuscate PowerShell scripts."),

        ("git+https://github.com/Donaldduck8/capa.git", "FLARE-Capa", "A tool to identify capabilities in executable files."),
        ("git+https://github.com/mandiant/speakeasy.git", "Speakeasy", "A comprehensive shellcode emulator and analysis toolkit."),

        # Frida
        ("frida-tools", "Frida Tools", "A collection of tools for the Frida instrumentation framework."),
        ("frida", "Frida Python Bindings", "Python bindings for Frida."),

        # Qiling
        ("https://github.com/qilingframework/qiling/archive/dev.zip", "Qiling", "A high-level emulation framework for Linux, Windows, and macOS."),
    ],

    "npm": [
        # Packages observed in malware samples
        ("axios", "axios", "A promise-based HTTP client for the browser and Node.js."),
        ("adm-zip", "adm-zip", "A zip library for NodeJS."),
        ("crypto", "crypto", "A package to provide cryptographic functionality."),
        ("sqlite3", "sqlite3", "A package to provide SQLite3 bindings."),
        ("systeminformation", "systeminformation", "A package to provide system information."),
        ("@primno/dpapi", "@primno/dpapi", "A package to provide DPAPI bindings."),

        # JavaScript deobfuscators (Dynamic)
        ("obfuscator-io-deobfuscator", "obfuscator.io Deobfuscator", "A tool to deobfuscate JavaScript from obfuscator.io."),
        ("js-deobfuscator", "js-deobfuscator", "A tool to deobfuscate JavaScript."),
        ("deobfuscator", "deobfuscator", "A tool to deobfuscate JavaScript."),
        ("git+https://github.com/HynekPetrak/malware-jail.git", "Malware Jail", "A tool to dynamically evaluate JavaScript to deobfuscate opaque predicates."),
        ("frida", "Frida", "A dynamic instrumentation toolkit for developers, reverse-engineers, and security researchers."),
    ],

    "ida_plugins": [
        ("https://github.com/OALabs/hashdb-ida/raw/main/hashdb.py", "HashDB", "A plugin to identify API hashing algorithms in malware samples."),
        ("https://github.com/mandiant/capa/raw/master/capa/ida/plugin/capa_explorer.py", "Capa Explorer", "A plugin to analyze and explore the capabilities of a malware sample."),
        ("https://github.com/fox-it/mkYARA/raw/master/mkyara/ida/mkyara_plugin.py", "mkYARA", "A plugin to generate YARA rules from malware samples."),
        ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/better_annotator.py", "Better Annotator", "A plugin to import decrypted strings into IDA Pro."),
        ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/donald_ida_plugin.py", "Donald IDA Plugin", "A hotkey to create a synchronized disassembly view."),
        ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/donald_ida_utils.py", "Donald IDA Utils", "A collection of utilities for IDA Pro."),
        ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/dump_bytes.py", "Dump Bytes", "A plugin to dump embedded blobs from malware samples."),
    ],

    "vscode_extensions": [
        ("ms-python.debugpy", "Python Debug", "A Python debugger for Visual Studio Code."),
        ("ms-python.python", "Python", "A Python language server for Visual Studio Code."),
        ("ms-python.vscode-pylance", "Pylance", "A Python language server for Visual Studio Code."),
        ("infosec-intern.yara", "Yara", "A YARA language server for Visual Studio Code."),
        ("ms-toolsai.jupyter", "Jupyter", "A Jupyter extension for Visual Studio Code."),
        ("akamud.vscode-theme-onedark", "One Dark Pro", "A dark theme for Visual Studio Code."),
        ("ms-vscode.powershell", "PowerShell", "A PowerShell extension for Visual Studio Code."),
    ],

    "taskbar_pins": [
        ("Microsoft.Windows.Explorer", "Windows Explorer", "The file manager for Windows."),
        ("%USERPROFILE%\\scoop\\apps\\chromium\\current\\chrome.exe", "Chromium", "A web browser that is the basis for Google Chrome."),
        ("%USERPROFILE%\\scoop\\apps\\sysinternals\\current\\procexp64.exe", "Process Explorer", "A tool to manage processes and system information."),
        ("%USERPROFILE%\\scoop\\apps\\sysinternals\\current\\procmon64.exe", "Process Monitor", "A tool to monitor system activity."),
        ("%USERPROFILE%\\scoop\\apps\\x64dbg\\current\\release\\x96dbg.exe", "x64dbg", "An open-source x64/x32 debugger for Windows."),
        ("%USERPROFILE%\\scoop\\apps\\ida*\\current\\ida64.exe", "IDA Pro", "A disassembler and debugger for analyzing binary files."),
        ("%USERPROFILE%\\scoop\\apps\\binary_nin*\\current\\binaryninja.exe", "Binary Ninja", "A reverse engineering platform."),
        ("%USERPROFILE%\\scoop\\apps\\vscode\\current\\Code.exe", "Visual Studio Code", "A code editor redefined and optimized for building and debugging modern web and cloud applications."),
        ("%USERPROFILE%\\scoop\\apps\\windows-terminal\\current\\wt.exe", "Windows Terminal", "A modern terminal application for users of command-line tools and shells."),
    ],

    "git_repositories": [
        ("https://github.com/Donaldduck8/fuxnet", "Fuxnet", "A collection of Python scripts to emulate various server types."),
        ("https://github.com/mandiant/capa-rules", "CAPA Rules", "A collection of rules for the Capa malware analysis framework."),
        ("https://github.com/HynekPetrak/malware-jail", "Malware Jail", "A tool to dynamically evaluate JavaScript to deobfuscate opaque predicates."),
        ("https://github.com/SentineLabs/AlphaGolang", "AlphaGolang", "A collection of scripts to reverse-engineer Go binaries."),
    ],

    "ida_py_switch": "%USERPROFILE%\\scoop\\apps\\python*\\current\\python3*.dll",

    "file_type_associations": {
        "Text": {
            "path": "%USERPROFILE%\\scoop\\apps\\sublime-text\\current\\sublime_text.exe",
            "program_name": "Sublime Text",
            "arguments": [],
            "file_types": [
                "txt",
                "log",
                "json",
                "xml",
                "csv",
                "ini",
                "cfg"
            ]
        },

        "Browser": {
            "path": "%USERPROFILE%\\scoop\\apps\\chromium\\current\\chrome.exe",
            "program_name": "Chromium",
            "arguments": [],
            "file_types": [
                "html",
                "htm",
                "shtml",
                "xht",
                "xhtml",
                "svg",
                "webp",
                "mhtml",
                "mht",
                "url",
                "webloc",
            ]
        },

        "Archive": {
            "path": "%USERPROFILE%\\scoop\\apps\\7zip\\current\\7zFM.exe",
            "program_name": "7-Zip",
            "arguments": [],
            "file_types": [
                "7z",
                "zip",
                "rar",
                "tar",
                "gz",
                "bz2",
                "xz",
                "iso",
            ]
        },

        "Java": {
            "path": "%USERPROFILE%\\scoop\\apps\\temurin17-jdk\\current\\bin\\java.exe",
            "program_name": "Java",
            "arguments": ["-jar"],
            "file_types": [
                "jar",
                "war",
                "ear",
            ]
        },
    },

    "registry_changes": {
        "Basics": [
            {
                "description": "Add NpCapInstaller to RunOnce to install Npcap after a reboot.",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce",
                "value": "NpCapInstaller",
                "data": "%USERPROFILE%\\scoop\\apps\\wireshark\\current\\npcap-installer.exe",
                "type": "REG_SZ"
            },
            {
                "description": "Enable dark mode for applications.",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                "value": "AppsUseLightTheme",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Remove the task view button from the taskbar.",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                "value": "ShowTaskViewButton",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Hide desktop icons.",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                "value": "HideIcons",
                "data": "1",
                "type": "REG_DWORD"
            },
            {
                "description": "Show full directory path in Explorer title bar",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\CabinetState",
                "value": "FullPath",
                "data": "1",
                "type": "REG_DWORD"
            },
            {
                "description": "Show known file extensions",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                "value": "HideFileExt",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Show hidden files",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
                "value": "Hidden",
                "data": "1",
                "type": "REG_DWORD"
            },
            {
                "description": "Disable SmartScreen",
                "hive": "HKEY_LOCAL_MACHINE",
                "key": "SOFTWARE\\Policies\\Microsoft\\Windows\\System",
                "value": "EnableSmartScreen",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Disable Microsoft Edge Phishing Filter",
                "hive": "HKEY_LOCAL_MACHINE",
                "key": "SOFTWARE\\Policies\\Microsoft\\MicrosoftEdge\\PhishingFilter",
                "value": "EnabledV9",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Disable Windows Firewall (Standard Profile)",
                "hive": "HKEY_LOCAL_MACHINE",
                "key": "SOFTWARE\\Policies\\Microsoft\\WindowsFirewall\\StandardProfile",
                "value": "EnableFirewall",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Fix rare error (0xd000003a) when opening Windows Terminal",
                "hive": "HKEY_LOCAL_MACHINE",
                "key": "SYSTEM\\CurrentControlSet\\Services\\condrv",
                "value": "Start",
                "data": "2",
                "type": "REG_DWORD"
            },
            {
                "description": "Disable search bar suggestions",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Policies\\Microsoft\\Windows",
                "value": "DisableSearchBoxSuggestions",
                "data": "1",
                "type": "REG_DWORD"
            },
            {
                "description": "Disable search bar widget",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Search",
                "value": "SearchboxTaskbarMode",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Use Taskbar Pins",
                "hive": "HKEY_CURRENT_USER",
                "key": "SOFTWARE\\Policies\\Microsoft\\Windows\\Explorer",
                "value": "LockedStartLayout",
                "data": "1",
                "type": "REG_DWORD"
            },
            {
                "description": "Use Taskbar Pins",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Microsoft\\Windows\\CurrentVersion\\Group Policy Objects\\{7810E935-4876-4362-BF9C-D1EA60BCBB24}User\\Software\\Policies\\Microsoft\\Windows\\Explorer",
                "value": "LockedStartLayout",
                "data": "1",
                "type": "REG_DWORD"
            },
            {
                "description": "Specify Taskbar Pins",
                "hive": "HKEY_CURRENT_USER",
                "key": "Software\\Policies\\Microsoft\\Windows\\Explorer",
                "value": "StartLayoutFile",
                "data": "%USERPROFILE%\\Documents\\startLayout.xml",
                "type": "REG_SZ"
            },
            {
                "description": "Remove OneDrive pin from the Explorer window",
                "hive": "HKEY_CLASSES_ROOT",
                "key": "CLSID\\{018D5C66-4533-4307-9B53-224DE2ED1FE6}",
                "value": "System.IsPinnedToNameSpaceTree",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Remove Taskbar Widgets",
                "hive": "HKEY_LOCAL_MACHINE",
                "key": "Software\\Policies\\Microsoft\\Dsh",
                "value": "AllowNewsAndInterests",
                "data": "0",
                "type": "REG_DWORD"
            },
            {
                "description": "Disable stupid ass path expansion in git Bash",
                "hive": "HKEY_CURRENT_USER",
                "key": "Environment",
                "value": "MSYS_NO_PATHCONV",
                "data": "1",
                "type": "REG_SZ"
            },
        ]
    },
    "misc_files": {
        "Yazi": [
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/yazi/init.lua",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/yazi/keymap.toml",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/yazi/theme.toml",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/yazi/yazi.toml"
                ],
                "target": "%APPDATA%\\yazi\\config"
            },
            {
                "description": "Donald's Previewer",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/yazi/plugins/donald.yazi/init.lua",
                ],
                "target": "%APPDATA%\\yazi\\config\\plugins\\donald.yazi"
            },
        ],
        "Zsh": [
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/zsh/.bash_profile",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/zsh/.bashrc",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/zsh/.p10k.zsh",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/zsh/.zshrc",
                ],
                "target": "%USERPROFILE%"
            },
        ],
        "VSCode": [
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/vscode_settings/settings.json",
                ],
                "target": "%USERPROFILE%\\scoop\\apps\\vscode\\current\\data\\user-data\\User"
            },
        ],
        "Terminal": [
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/terminal/settings.json",
                ],
                "target": "%USERPROFILE%\\scoop\\apps\\windows-terminal\\current\\settings"
            },
        ],
        "Sublime Text": [
            {
                "description": "Theme",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/sublime_packages/Packages/tokyonight_night.tmTheme",
                ],
                "target": "%USERPROFILE%\\scoop\\apps\\sublime-text\\current\\Data\\Packages"
            },
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/sublime_packages/Packages/User/Preferences.sublime-settings",
                ],
                "target": "%USERPROFILE%\\scoop\\apps\\sublime-text\\current\\Data\\Packages\\User"
            },
        ],
        "GlazeWM": [
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/glazewm_configuration/config.yaml",
                ],
                "target": "%USERPROFILE%\\.glaze-wm"
            },
        ],
        "Scripts": [
            {
                "description": "Malware Intake",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/scripts/malware_intake.py",
                ],
                "target": "%USERPROFILE%\\scripts"
            },
        ],
        "Chromium": [
            {
                "description": "Configuration",
                "sources": [
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/chromium_bookmarks/Bookmarks",
                    "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/chromium_bookmarks/Preferences",
                ],
                "target": "%LOCALAPPDATA%\\Chromium\\User Data\\Default"
            },
        ]
    },
}

# Sort the entries of the configuration dictionary for OCD

def key_lambda(x):
    if isinstance(x, str):
        return x
    elif isinstance(x, tuple) or isinstance(x, list):
        return x[1]
    elif isinstance(x, dict) and x["type"] == "one_of":
        return x["main"][1]
    else:
        raise ValueError(f"Unknown type: {type(x)}")

# Sort everything alphabetically
for key in default_configuration["scoop"]:
    if isinstance(default_configuration["scoop"][key], list):
        default_configuration["scoop"][key] = natsorted(default_configuration["scoop"][key], key=key_lambda, alg=ns.IGNORECASE)

for key in default_configuration["registry_changes"]:
    if isinstance(default_configuration["registry_changes"][key], list):
        default_configuration["registry_changes"][key] = natsorted(default_configuration["registry_changes"][key], key=lambda x: x["description"], alg=ns.IGNORECASE)

default_configuration["pip"] = natsorted(default_configuration["pip"], key=key_lambda, alg=ns.IGNORECASE)
default_configuration["npm"] = natsorted(default_configuration["npm"], key=key_lambda, alg=ns.IGNORECASE)
default_configuration["ida_plugins"] = natsorted(default_configuration["ida_plugins"], key=key_lambda, alg=ns.IGNORECASE)
default_configuration["vscode_extensions"] = natsorted(default_configuration["vscode_extensions"], key=key_lambda, alg=ns.IGNORECASE)
default_configuration["git_repositories"] = natsorted(default_configuration["git_repositories"], key=key_lambda, alg=ns.IGNORECASE)

default_configuration = json.loads(json.dumps(default_configuration))

# Keep track of the default configuration
configuration = default_configuration.copy()

# Validation logic for custom configurations
def validate_bucket_item(item):
    """ Validate individual bucket items. """
    return isinstance(item, tuple) and len(item) == 3 and all(isinstance(i, str) for i in item)

def validate_item(item):
    if isinstance(item, str):
        return True
    
    elif isinstance(item, tuple) or isinstance(item, list):
        if len(item) != 3:
            raise RuntimeError(f"Item does not have precisely three entries (id, title, description): {item}")
        
        if not all(isinstance(i, str) for i in item):
            raise RuntimeError(f"Item does not contain all strings: {item}")
        
        return True
    
    elif isinstance(item, dict):
        if not all(k in item for k in ["type", "main", "alternative"]):
            raise RuntimeError(f"Item does not contain all required keys (type, main, alternative): {item}")

        if not isinstance(item["type"], str) or not item["type"] == "one_of":
            raise RuntimeError(f"Item does not contain a valid type field: {item}")
        
        if not validate_item(item["main"]) or not validate_item(item["alternative"]):
            raise RuntimeError(f"Item does not contain valid main or alternative fields: {item}")
        
        return True
    

def validate_registry_change_item(item):
    if not isinstance(item, dict):
        raise RuntimeError(f"Registry change item is not a dictionary: {item}")
    
    if not all(k in item for k in ["description", "hive", "key", "value", "data", "type"]):
        raise RuntimeError(f"Registry change item does not contain all required keys (description, hive, key, value, data, type): {item}")
    
    if not all(isinstance(item[k], str) for k in ["description", "hive", "key", "value", "data", "type"]):
        raise RuntimeError(f"Registry change item does not contain all strings: {item}")
    
    # Check hive
    if item["hive"] not in [
        "HKEY_CLASSES_ROOT",
        "HKEY_CURRENT_USER", 
        "HKEY_LOCAL_MACHINE",
        "HKEY_USERS",
        "HKEY_CURRENT_CONFIG",
    ]:
        raise RuntimeError(f"Registry change item contains invalid hive: {item}")
    
    # Check type
    if item["type"] not in [
        "REG_SZ", 
        "REG_DWORD",
        "REG_BINARY",
        "REG_EXPAND_SZ",
        "REG_MULTI_SZ",
        "REG_QWORD",
    ]:
        raise RuntimeError(f"Registry change item contains invalid type: {item}")
    
    return True


def validate_fta_item(item):
    if not isinstance(item, dict):
        raise RuntimeError(f"File type association item is not a dictionary: {item}")
    
    if not all(k in item for k in ["path", "program_name", "arguments", "file_types"]):
        raise RuntimeError(f"File type association item does not contain all required keys (path, program_name, arguments, file_types): {item}")
    
    if not all(isinstance(item[k], str) for k in ["path", "program_name"]) or not isinstance(item["arguments"], list):
        raise RuntimeError(f"File type association item does not contain all strings: {item}")
    
    if not isinstance(item["file_types"], list) or not all(isinstance(i, str) for i in item["file_types"]):
        raise RuntimeError(f"File type association item does not contain all strings in file_types: {item}")
    
    if not isinstance(item["arguments"], list) or not all(isinstance(i, str) for i in item["arguments"]):
        raise RuntimeError(f"File type association item does not contain all strings in arguments: {item}")
    
    return True


def validate_misc_files_item(item):
    if not isinstance(item, dict):
        raise RuntimeError(f"Miscellaneous files item is not a dictionary: {item}")
    
    if not all(k in item for k in ["description", "sources", "target"]):
        raise RuntimeError(f"Miscellaneous files item does not contain all required keys (description, sources, target): {item}")
    
    if not isinstance(item["description"], str) or not isinstance(item["sources"], list) or not isinstance(item["target"], str):
        raise RuntimeError(f"Miscellaneous files item does not contain all strings: {item}")
    
    if not isinstance(item["sources"], list) or not all(isinstance(i, str) for i in item["sources"]):
        raise RuntimeError(f"Miscellaneous files item does not contain all strings in sources: {item}")
    
    return True


def validate_configuration(custom_config, default_config):
    """ Validate the entire configuration against the default configuration. """
    # Ensure all top-level keys are present
    default_keys = set(default_config.keys())
    custom_keys = set(custom_config.keys())

    if default_keys != custom_keys:
        raise RuntimeError(f"Missing or unexpected keys in custom configuration: {default_keys ^ custom_keys}")

    for _category, list_of_items in custom_config["scoop"].items():
        for i in list_of_items:
            validate_item(i)

    for i in custom_config["pip"]:
        validate_item(i)

    for i in custom_config["npm"]:
        validate_item(i)

    for i in custom_config["ida_plugins"]:
        validate_item(i)

    for i in custom_config["vscode_extensions"]:
        validate_item(i)

    for i in custom_config["git_repositories"]:
        validate_item(i)

    for _category, list_of_items in custom_config["registry_changes"].items():
        for i in list_of_items:
            validate_registry_change_item(i)

    for _category, i in custom_config["file_type_associations"].items():
        validate_fta_item(i)

    for _category, list_of_items in custom_config["misc_files"].items():
        for i in list_of_items:
            validate_misc_files_item(i)

    return True

# Validate the default configuration
validate_configuration(default_configuration, default_configuration)

# TODO: qiling
# TODO: https://github.com/last-byte/PersistenceSniper/releases/tag/v1.16.0
# sudo Install-Module PersistenceSniper
# sudo Import-Module PersistenceSniper
# sudo Find-AllPersistence -Verbose

# TODO: https://github.com/struppigel/hedgehog-tools/blob/main/ECMAScript%20helpers/extract_called_functions.js
# npm.exe install -save-dev @babel/core commander

# TODO: https://github.com/fkling/astexplorer