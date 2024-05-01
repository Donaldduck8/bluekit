import winreg

from dataclasses import dataclass


VERSION = "1.0.0"

@dataclass
class BasePackageStructure():
    id: str
    name: str
    description: str

@dataclass
class BasePackageListStructure():
    def parse_list_of(self, clazz, items):
        return [clazz(**item) if isinstance(item, dict) else clazz(*item) for item in items]

@dataclass
class ScoopPackage(BasePackageStructure):
    alternative: BasePackageStructure

    def __init__(self, id, name, description, alternative=None):  # pylint: disable=redefined-builtin
        super().__init__(id, name, description)
        if alternative:
            self.alternative = BasePackageStructure(**alternative) if isinstance(alternative, dict) else BasePackageStructure(*alternative)
        else:
            self.alternative = None

@dataclass
class ScoopPackages(BasePackageListStructure):
    buckets: list[BasePackageStructure]
    required: list[ScoopPackage]
    packages: dict[str, list[ScoopPackage]]

    def __init__(self, buckets, required, packages):
        self.buckets = self.parse_list_of(BasePackageStructure, buckets)
        self.required = self.parse_list_of(ScoopPackage, required)
        self.packages = {group: self.parse_list_of(ScoopPackage, items) for group, items in packages.items()}

@dataclass
class PipPackage(BasePackageStructure):
    mode: str

    def __init__(self, id, name, description, mode="pip"):  # pylint: disable=redefined-builtin
        super().__init__(id, name, description)
        self.mode = mode

@dataclass
class PipPackages(BasePackageListStructure):
    required: list[PipPackage]
    packages: list[PipPackage]

    def __init__(self, required, packages):
        self.required = self.parse_list_of(PipPackage, required)
        self.packages = self.parse_list_of(PipPackage, packages)

@dataclass
class NpmPackage(BasePackageStructure):
    pass

@dataclass
class NpmPackages(BasePackageListStructure):
    packages: list[NpmPackage]

    def __init__(self, packages):
        self.packages = self.parse_list_of(NpmPackage, packages)

@dataclass
class IdaPlugin(BasePackageStructure):
    pass

@dataclass
class IdaPlugins(BasePackageListStructure):
    plugins: list[IdaPlugin]

    def __init__(self, plugins):
        self.plugins = self.parse_list_of(IdaPlugin, plugins)

@dataclass
class VscodeExtension(BasePackageStructure):
    pass

@dataclass
class VscodeExtensions(BasePackageListStructure):
    extensions: list[VscodeExtension]

    def __init__(self, extensions):
        self.extensions = self.parse_list_of(VscodeExtension, extensions)

@dataclass
class TaskbarPin(BasePackageStructure):
    pass

@dataclass
class TaskbarPins(BasePackageListStructure):
    pins: list[TaskbarPin]

    def __init__(self, pins):
        self.pins = self.parse_list_of(TaskbarPin, pins)

@dataclass
class GitRepository(BasePackageStructure):
    pass

@dataclass
class GitRepositories(BasePackageListStructure):
    repositories: list[GitRepository]

    def __init__(self, repositories):
        self.repositories = self.parse_list_of(GitRepository, repositories)

@dataclass
class FileTypeAssociation():
    path: str
    program_name: str
    arguments: list[str]
    file_types: list[str]

@dataclass
class FileTypeAssociations(BasePackageListStructure):
    associations: dict[str, FileTypeAssociation]

    def __init__(self, associations):
        self.associations = {group: FileTypeAssociation(**item) for group, item in associations.items()}

@dataclass
class RegistryChange():
    description: str
    hive: str
    key: str
    value: str
    data: str
    type: str

    def __init__(self, description, hive, key, value, data, type):  # pylint: disable=redefined-builtin
        # Validate hive and type
        if hive not in ["HKEY_CLASSES_ROOT", "HKEY_CURRENT_USER", "HKEY_LOCAL_MACHINE", "HKEY_USERS", "HKEY_CURRENT_CONFIG"]:
            raise ValueError(f"Invalid hive: {hive}")

        # Convert hive to winreg constant
        self.hive = getattr(winreg, hive)

        if type not in ["REG_SZ", "REG_EXPAND_SZ", "REG_MULTI_SZ", "REG_DWORD", "REG_QWORD", "REG_BINARY"]:
            raise ValueError(f"Invalid type: {type}")

        # Convert type to winreg constant
        self.type = getattr(winreg, type)

        self.description = description
        self.key = key
        self.value = value
        self.data = data


@dataclass
class RegistryChanges(BasePackageListStructure):
    changes: dict[str, list[RegistryChange]]

    def __init__(self, changes):
        # Parse each group of changes
        self.changes = {group: self.parse_list_of(RegistryChange, items) for group, items in changes.items()}


@dataclass
class MiscFile():
    description: str
    sources: list[str]
    target: str

@dataclass
class MiscFiles(BasePackageListStructure):
    files: dict[str, list[MiscFile]]

    def __init__(self, files):
        # Parse each group of files
        self.files = {group: [MiscFile(**item) for item in items] for group, items in files.items()}

@dataclass
class BluekitSettings():
    enable_windows_safer: bool
    malware_folders: list[str]
    ida_py_switch: str
    install_zsh_over_git: bool
    make_bindiff_available: bool

@dataclass
class Configuration():
    scoop: ScoopPackages
    pip: PipPackages
    npm: NpmPackages
    ida_plugins: IdaPlugins
    vscode_extensions: VscodeExtensions
    taskbar_pins: TaskbarPins
    git_repositories: GitRepositories
    file_type_associations: FileTypeAssociations
    registry_changes: RegistryChanges
    misc_files: MiscFiles
    settings: BluekitSettings

    def __init__(self, scoop, pip, npm, ida_plugins, vscode_extensions, taskbar_pins, git_repositories, file_type_associations, registry_changes, misc_files, settings):
        if scoop is not None:
            self.scoop = ScoopPackages(**scoop)

        if pip is not None:
            self.pip = PipPackages(**pip)

        if npm is not None:
            self.npm = NpmPackages(**npm)

        if ida_plugins is not None:
            self.ida_plugins = IdaPlugins(**ida_plugins)

        if vscode_extensions is not None:
            self.vscode_extensions = VscodeExtensions(**vscode_extensions)

        if taskbar_pins is not None:
            self.taskbar_pins = TaskbarPins(**taskbar_pins)

        if git_repositories is not None:
            self.git_repositories = GitRepositories(**git_repositories)

        if file_type_associations is not None:
            self.file_type_associations = FileTypeAssociations(**file_type_associations)

        if registry_changes is not None:
            self.registry_changes = RegistryChanges(**registry_changes)

        if misc_files is not None:
            self.misc_files = MiscFiles(**misc_files)

        if settings is not None:
            self.settings = BluekitSettings(**settings)

    @classmethod
    def empty(cls):
        return cls(None, None, None, None, None, None, None, None, None, None, None)

default_configuration = {
    "scoop": {
        "buckets": [
            ("extras", "Extras", "Extra software that doesn't fit in the main bucket."),
            ("versions", "Versions", "Older versions of software."),
            ("nerd-fonts", "Nerd Fonts", "Patched fonts with a high number of glyphs."),
            ("java", "Java", "Java Development Kit and Java Runtime Environment."),
            ("malware-analysis-bucket https://github.com/Donaldduck8/malware-analysis-bucket", "Malware Analysis Bucket", "Tools for analyzing malware."),
        ],

        "required": [
            ("git", "Git", "A distributed version control system."),
            ("pwsh", "PowerShell", "A task automation and configuration management framework."),

            # No-pollute version because Python2 is only used for Krakatoa
            ("malware-analysis-bucket/python27-no-pollute", "Python 2.7", "The newest Python 2.x version available, required for Java bytecode editing."),

            ("python311", "Python 3.11", "The newest Python version currently compatible with IDA Pro."),
            ("malware-analysis-bucket/portable_build_tools", "Portable Build Tools", "A portable version of Visual C++ build tools."),
            ("zulufx17-jdk", "Zulu JDK FX 17", "A Java Development Kit with JavaFX 17."),
        ],

        "packages": {
            "Basics": [
                # Basics
                ("FiraCode-NF-Mono", "Fira Code (Mono)", "A monospaced font with programming ligatures."),
                ("chromium", "Chromium", "A web browser that is the basis for Google Chrome."),
                ("sublime-text", "Sublime Text", "A sophisticated text editor for code, markup, and prose."),
                ("7zip", "7-Zip", "A file archiver with a high compression ratio."),
                ("vscodium", "Codium", "A code editor redefined and optimized for building and debugging modern web and cloud applications."),
            ],

            "Miscellaneous": [
                ("malware-analysis-bucket/glazewm_extra", "Glaze Window Manager", "A tiling window manager for Windows."),
                ("setuserfta", "SetUserFTA", "A tool to change the default program associated with a file type."),
                ("upx", "UPX", "A free, portable, extendable, high-performance executable packer for several executable formats."),

                # No pollute version because otherwise, x64dbg plugin manager will mysteriously fail to install.
                ("malware-analysis-bucket/openssl-light-no-pollute", "OpenSSL", "A robust, commercial-grade, and full-featured toolkit for TLS and SSL."),

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
                    "id": "ida_pro.json", 
                    "name": "IDA Pro", 
                    "description": "A disassembler and debugger for analyzing binary files.",
                    "alternative": ("ida-free", "IDA Free", "A free version of IDA Pro.")
                },
                {
                    "id": "binary_ninja.json", 
                    "name": "Binary Ninja",
                    "description": "A reverse engineering platform.",
                    "alternative": ("malware-analysis-bucket/binary_ninja_free", "Binary Ninja Free", "A free version of Binary Ninja."),
                },
                ("ghidra", "Ghidra", "A software reverse engineering (SRE) framework."),
                ("malware-analysis-bucket/ghidrathon-np", "Ghidrathon", "A tool to use Python within Ghidra."),
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
                ("malware-analysis-bucket/fakenet", "Fakenet-NG", "A tool to analyze network traffic."),
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
                ("malware-analysis-bucket/goresym", "GoResym", "A Golang symbol parser that extracts metadata, embedded structures and types."),
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
                    "id": "linqpad_pro.json",
                    "name": "LINQPad",
                    "description": "A tool to easily write C# scripts to interact with .NET malware samples.",
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

            # JAVA (Static)
            "JAVA (Static)": [
                ("malware-analysis-bucket/recaf3", "Recaf 3.0.0-SNAPSHOT", "A snapshot of the current state of development of Recaf 3, which is a modern Java bytecode viewer and decompiler."),
                ("malware-analysis-bucket/recaf4", "Recaf 4.0.0-SNAPSHOT", "A snapshot of the current state of development of Recaf 4, which is a modern Java bytecode viewer and decompiler."),
                ("malware-analysis-bucket/java-disassembler", "Java Disassembler", "A tool to disassemble Java class files."),
                ("malware-analysis-bucket/java-deobfuscator", "Java Deobfuscator", "A tool to deobfuscate Java class files."),
                ("cfr", "CFR", "A Java decompiler."),
                ("procyon", "Procyon", "A Java decompiler."),
                ("malware-analysis-bucket/fernflower", "Fernflower", "A Java decompiler."),
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
            "Rust" : [
                ("rustup", "Rustup", "A tool to manage Rust installations."),  # Relies on Visual C++ build tools
            ],

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
        }
    },

    "pip": {
        "required": [
            ("binary-refinery[all]", "Binary Refinery", "A collection of tools for reverse engineering, binary analysis and pipeline creation.", "pipx"),
        ],

        "packages": [
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
            ("git+https://github.com/Donaldduck8/rustbinsign", "RustBinSign", "A tool to generate FLIRT / SIGKIT signatures from Rust binaries.", "pipx"),

            # Donut Shellcode
            ("git+https://github.com/volexity/chaskey-lts", "chaskey-lts", "A Python implementation of the Chaskey-LTS block cipher."),
            ("git+https://github.com/volexity/donut-decryptor", "donut-decryptor", "A tool to decrypt Donut shellcode."),

            # D810
            ("z3-solver", "z3-solver", "A theorem prover from Microsoft Research."),

            # Python
            ("uncompyle6", "uncompyle6", "A Python bytecode decompiler.", "pipx"),
            ("decompyle3", "decompyle3", "A Python bytecode decompiler.", "pipx"),

            # PowerShell (Static)
            ("git+https://github.com/Donaldduck8/deobshell@pip-installable", "deobshell", "A tool to statically deobfuscate PowerShell scripts.", "pipx"),

            ("flare-capa", "FLARE-Capa", "A tool to identify capabilities in executable files."),
            ("git+https://github.com/mandiant/speakeasy", "Speakeasy", "A comprehensive shellcode emulator and analysis toolkit.", "pipx"),

            # Frida
            ("frida-tools", "Frida Tools", "A collection of tools for the Frida instrumentation framework."),
            ("frida", "Frida Python Bindings", "Python bindings for Frida."),

            # Qiling
            ("https://github.com/qilingframework/qiling/archive/dev.zip", "Qiling", "A high-level emulation framework for Linux, Windows, and macOS."),

            # Fuxnet
            ("netifaces", "netifaces", "A package to query network interfaces."),

            # Ghidrathon
            ("jep", "Jep", "A Python-Java bridge."),
        ]
    },

    "npm": {
        "packages": [
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
            # ("git+https://github.com/Donaldduck8/malware-jail#npm-installable", "Malware Jail", "A tool to dynamically evaluate JavaScript to deobfuscate opaque predicates."),
            # ("frida", "Frida", "A dynamic instrumentation toolkit for developers, reverse-engineers, and security researchers."),  # Requires Visual C++ build tools, currently does not work

            # ("webcrack", "WebCrack", "A tool to deobfuscate JavaScript."),  # Requires Visual C++ build tools, currently does not work

            # Required by Hedgehog Tools
            ("@babel/core", "@babel/core", "A tool to compile JavaScript."),
            ("commander", "commander", "A tool to create command-line interfaces in Node.js."),
        ]
    },

    "ida_plugins": {
        "plugins": [
            ("https://github.com/OALabs/hashdb-ida/raw/main/hashdb.py", "HashDB", "A plugin to identify API hashing algorithms in malware samples."),
            ("https://github.com/mandiant/capa/raw/master/capa/ida/plugin/capa_explorer.py", "Capa Explorer", "A plugin to analyze and explore the capabilities of a malware sample."),
            ("https://github.com/fox-it/mkYARA/raw/master/mkyara/ida/mkyara_plugin.py", "mkYARA", "A plugin to generate YARA rules from malware samples."),
            ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/better_annotator.py", "Better Annotator", "A plugin to import decrypted strings into IDA Pro."),
            ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/donald_ida_plugin.py", "Donald IDA Plugin", "A hotkey to create a synchronized disassembly view."),
            ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/donald_ida_utils.py", "Donald IDA Utils", "A collection of utilities for IDA Pro."),
            ("https://github.com/Donaldduck8/IDA-Scripts-and-Tools/raw/master/dump_bytes.py", "Dump Bytes", "A plugin to dump embedded blobs from malware samples."),
        ]
    },

    "vscode_extensions": {
        "extensions": [
            ("ms-python.debugpy", "Python Debug", "A Python debugger for Visual Studio Code."),
            ("ms-python.python", "Python", "A Python language server for Visual Studio Code."),
            ("infosec-intern.yara", "Yara", "A YARA language server for Visual Studio Code."),
            ("akamud.vscode-theme-onedark", "One Dark Pro", "A dark theme for Visual Studio Code."),
            ("ms-vscode.powershell", "PowerShell", "A PowerShell extension for Visual Studio Code."),
            ("vscjava.vscode-java-pack", "Java Extension Pack", "A collection of popular Java extensions for Visual Studio Code."),
        ]
    },

    "taskbar_pins": {
        "pins": [
            ("Microsoft.Windows.Explorer", "Windows Explorer", "The file manager for Windows."),
            ("%USERPROFILE%\\scoop\\apps\\chromium\\current\\chrome.exe", "Chromium", "A web browser that is the basis for Google Chrome."),
            ("%USERPROFILE%\\scoop\\apps\\sysinternals\\current\\procexp64.exe", "Process Explorer", "A tool to manage processes and system information."),
            ("%USERPROFILE%\\scoop\\apps\\sysinternals\\current\\procmon64.exe", "Process Monitor", "A tool to monitor system activity."),
            ("%USERPROFILE%\\scoop\\apps\\x64dbg\\current\\release\\x96dbg.exe", "x64dbg", "An open-source x64/x32 debugger for Windows."),
            ("%USERPROFILE%\\scoop\\apps\\ida*\\current\\ida64.exe", "IDA Pro", "A disassembler and debugger for analyzing binary files."),
            ("%USERPROFILE%\\scoop\\apps\\binary_nin*\\current\\binaryninja.exe", "Binary Ninja", "A reverse engineering platform."),
            ("%USERPROFILE%\\scoop\\apps\\vscode\\current\\Code.exe", "Visual Studio Code", "A code editor redefined and optimized for building and debugging modern web and cloud applications."),
            ("%USERPROFILE%\\scoop\\apps\\windows-terminal\\current\\wt.exe", "Windows Terminal", "A modern terminal application for users of command-line tools and shells."),
        ]
    },

    "git_repositories": {
        "repositories": [
            ("https://github.com/Donaldduck8/fuxnet", "Fuxnet", "A collection of Python scripts to emulate various server types."),
            ("https://github.com/mandiant/capa-rules", "CAPA Rules", "A collection of rules for the Capa malware analysis framework."),
            ("https://github.com/SentineLabs/AlphaGolang", "AlphaGolang", "A collection of scripts to reverse-engineer Go binaries."),
            ("https://github.com/struppigel/hedgehog-tools", "Hedgehog Tools", "A collection of tools for reverse engineering and malware analysis, written by Karsten Hahn."),
            ("https://github.com/HynekPetrak/malware-jail", "Malware Jail", "A tool to dynamically evaluate JavaScript to deobfuscate opaque predicates."),
            ("https://github.com/Fadi002/de4py", "de4py", "A toolkit for Python reverse engineering."),
        ]
    },

    "file_type_associations": {
        "associations": {
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
                "path": "%USERPROFILE%\\scoop\\apps\\zulufx17-jdk\\current\\bin\\java.exe",
                "program_name": "Java",
                "arguments": ["-jar"],
                "file_types": [
                    "jar",
                    "war",
                    "ear",
                ]
            },
        }
    },

    "registry_changes": {
        "changes": {
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
                {
                    "description": "Make distutils use Windows SDK to enable portable build tools",
                    "hive": "HKEY_CURRENT_USER",
                    "key": "Environment",
                    "value": "DISTUTILS_USE_SDK",
                    "data": "1",
                    "type": "REG_SZ"
                },
            ]
        }
    },
    "misc_files": {
        "files": {
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
                {
                    "description": "Ouch Previewer",
                    "sources": [
                        "https://github.com/ndtoan96/ouch.yazi/raw/main/init.lua",
                    ],
                    "target": "%APPDATA%\\yazi\\config\\plugins\\ouch.yazi"
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
                {
                "description": "Configuration (Codium)",
                    "sources": [
                        "https://github.com/Donaldduck8/malware-analysis-configurations/raw/main/vscode_settings/settings.json",
                    ],
                    "target": "%USERPROFILE%\\scoop\\apps\\vscodium\\current\\data\\user-data\\User"
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
        }
    },
    "settings": {
        "enable_windows_safer": True,
        "malware_folders": [
            "%USERPROFILE%\\malware"
        ],
        "ida_py_switch": "%USERPROFILE%\\scoop\\apps\\python*\\current\\python3*.dll",
        "install_zsh_over_git": True,
        "make_bindiff_available": True,
    }
}

configuration = Configuration(**default_configuration)

# Other tools that I would like to add:
# qiling
# PersistenceSniper

# https://github.com/fkling/astexplorer

# https://github.com/stong/maple-ir/tree/ubsan

# How to deal with javascript malware that requires ActiveXObject?

# Narumii

# Find out how to add Mono.Cecil to Linqpad automatically

# malware-jail broken
# js-deobfuscator broken
