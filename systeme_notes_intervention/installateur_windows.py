from __future__ import annotations

import argparse
import ctypes
import json
import os
import platform
import shutil
import subprocess
import sys
import threading
import time
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


APP_NAME = "Easy CESU"
EXE_NAME = "Easy CESU.exe"
APP_VERSION = "3.1.1"
APP_ID = "EasyCESU.Windows.x64"
NOTICE_NAME = "Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf"
WEBVIEW2_BOOTSTRAPPER_NAME = "MicrosoftEdgeWebview2Setup.exe"
WEBVIEW2_CLIENT_ID = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
LEGACY_APP_NAMES = ["Factures Cloclo"]
SHORTCUT_ICON_LABELS = {
    "generique": "Services à la personne - générique",
    "jardinage": "Jardinage - icône actuelle",
    "bricolage": "Bricolage",
    "menage": "Ménage",
    "aide_a_domicile": "Aide à domicile",
    "garde_d_enfants": "Garde d'enfants",
    "soutien_scolaire": "Soutien scolaire",
    "accompagnement": "Accompagnement",
    "assistance_administrative": "Assistance administrative",
    "informatique": "Informatique à domicile",
}


def shortcut_label() -> str:
    major, minor, patch = (APP_VERSION.split(".") + ["0", "0"])[:3]
    return f"{APP_NAME} V{major}" if minor == "0" and patch == "0" else f"{APP_NAME} V{APP_VERSION}"


def program_files_root() -> Path:
    return Path(os.environ.get("ProgramFiles") or r"C:\Program Files")


def default_destination() -> Path:
    return program_files_root() / APP_NAME


def user_data_destination() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "EasyCESU"


def legacy_local_install_destination() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / APP_NAME


def installer_log_path() -> Path:
    return user_data_destination() / "logs" / "installer.log"


def log_installation(message: str) -> None:
    path = installer_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {message}\n")


def ensure_windows_x64() -> None:
    machine = platform.machine().casefold()
    if os.name != "nt" or machine not in {"amd64", "x86_64"}:
        raise RuntimeError("Cette version de Easy CESU est réservée à Windows 11 x64.")


def is_admin() -> bool:
    if os.name != "nt":
        return True
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def protected_install_roots() -> list[Path]:
    roots = [program_files_root()]
    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    system_root = os.environ.get("SystemRoot") or os.environ.get("WINDIR")
    if program_files_x86:
        roots.append(Path(program_files_x86))
    if system_root:
        roots.append(Path(system_root))
    return roots


def is_relative_to_path(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def requires_elevation(destination: Path) -> bool:
    if os.name != "nt":
        return False
    return any(is_relative_to_path(destination, root) for root in protected_install_roots())


def has_existing_installation(folder: Path) -> bool:
    return (folder / EXE_NAME).exists() or (folder / "_internal").exists()


def shortcut_target(shortcut_path: Path) -> Path | None:
    if not shortcut_path.exists():
        return None
    script = """
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($env:SHORTCUT_PATH)
Write-Output $Shortcut.TargetPath
"""
    env = os.environ.copy()
    env["SHORTCUT_PATH"] = str(shortcut_path)
    try:
        completed = subprocess.run(
            [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except Exception:
        return None
    target = completed.stdout.strip()
    return Path(target) if target else None


def unique_install_destination(base: Path) -> Path:
    if not base.exists():
        return base
    parent = base.parent
    name = base.name
    index = 2
    while True:
        candidate = parent / f"{name} {index}"
        if not candidate.exists():
            return candidate
        index += 1


def detect_existing_installations(destination: Path) -> list[Path]:
    candidates = [
        destination,
        default_destination(),
        legacy_local_install_destination(),
        user_data_destination(),
    ]
    programs = start_menu_programs_path()
    shortcut_paths = [
        desktop_path() / f"{APP_NAME}.lnk",
        Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop" / f"{APP_NAME}.lnk",
        start_menu_path() / f"{APP_NAME}.lnk",
        *desktop_path().glob(f"{APP_NAME} V*.lnk"),
        *start_menu_path().glob(f"{APP_NAME} V*.lnk"),
        *programs.glob(f"{APP_NAME}*.lnk"),
    ]
    for shortcut in shortcut_paths:
        target = shortcut_target(shortcut)
        if target:
            candidates.append(target.parent)

    found: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = candidate.expanduser().resolve(strict=False)
        key = str(resolved).casefold()
        if key in seen:
            continue
        seen.add(key)
        if has_existing_installation(resolved):
            found.append(resolved)
    return found


def choose_replacement_target(selected_destination: Path, existing: list[Path]) -> Path:
    selected = selected_destination.expanduser().resolve(strict=False)
    for item in existing:
        if item.resolve(strict=False) == selected:
            return selected
    return existing[0] if existing else selected


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "payload" / APP_NAME
    return Path(__file__).resolve().parent / "dist" / APP_NAME


def webview2_bootstrapper_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / WEBVIEW2_BOOTSTRAPPER_NAME
    return Path(__file__).resolve().parent / "build" / "dependencies" / WEBVIEW2_BOOTSTRAPPER_NAME


def webview2_runtime_version() -> str:
    """Retourne la version Evergreen installée, ou une chaîne vide."""

    if os.name != "nt":
        return ""
    import winreg

    locations = (
        (
            winreg.HKEY_LOCAL_MACHINE,
            rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}",
        ),
        (
            winreg.HKEY_CURRENT_USER,
            rf"Software\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}",
        ),
        (
            winreg.HKEY_LOCAL_MACHINE,
            rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{WEBVIEW2_CLIENT_ID}",
        ),
    )
    for root, key_path in locations:
        try:
            with winreg.OpenKey(root, key_path) as key:
                version = str(winreg.QueryValueEx(key, "pv")[0] or "").strip()
                if version and version != "0.0.0.0":
                    return version
        except OSError:
            continue
    return ""


def ensure_webview2_runtime() -> str:
    """Installe WebView2 silencieusement seulement s'il manque."""

    version = webview2_runtime_version()
    if version:
        return version
    bootstrapper = webview2_bootstrapper_path()
    if not bootstrapper.exists():
        raise RuntimeError(
            "Le composant Microsoft WebView2 est absent et son programme d'installation est introuvable."
        )
    completed = subprocess.run(
        [str(bootstrapper), "/silent", "/install"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        raise RuntimeError(
            "Microsoft WebView2 n'a pas pu être installé. "
            "Vérifie la connexion internet ou les règles de sécurité Windows."
        )
    for _ in range(60):
        version = webview2_runtime_version()
        if version:
            return version
        time.sleep(1)
    raise RuntimeError("Microsoft WebView2 a été lancé, mais son installation n'a pas été détectée.")


def installer_icon_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "easy-cesu.ico"
    return Path(__file__).resolve().parent / "application" / "assets" / "easy-cesu.ico"


def shortcut_icons_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "shortcut-icons"
    return Path(__file__).resolve().parent / "application" / "assets" / "shortcut-icons"


def normalize_shortcut_icon(value: str | None) -> str:
    key = str(value or "").strip().casefold()
    return key if key in SHORTCUT_ICON_LABELS else "generique"


def configured_shortcut_icon() -> str:
    """Reprend automatiquement le métier du compte actif lors d'une mise à jour."""
    config_path = user_data_destination() / "config" / "config.json"
    if not config_path.exists():
        return "generique"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        profiles = config.get("profiles") or []
        active_id = config.get("active_profile_id")
        profile = next((item for item in profiles if item.get("id") == active_id), profiles[0] if profiles else {})
        if profile.get("shortcut_icon") in SHORTCUT_ICON_LABELS:
            return normalize_shortcut_icon(profile.get("shortcut_icon"))
        return normalize_shortcut_icon(profile.get("primary_activity"))
    except (OSError, ValueError, TypeError):
        return "generique"


def shortcut_icon_source_path(icon_key: str) -> Path:
    key = normalize_shortcut_icon(icon_key)
    return shortcut_icons_root() / f"{key}.ico"


def shortcut_icon_preview_path(icon_key: str) -> Path:
    key = normalize_shortcut_icon(icon_key)
    return shortcut_icons_root() / f"{key}-preview.png"


def install_shortcut_icon(destination: Path, icon_key: str) -> Path | None:
    source = shortcut_icon_source_path(icon_key)
    if not source.exists():
        source = shortcut_icon_source_path("generique")
    if not source.exists():
        return None
    target = destination / "icons" / source.name
    target.parent.mkdir(parents=True, exist_ok=True)
    copy_file_with_retry(source, target)
    return target


def remember_shortcut_icon(icon_key: str) -> None:
    """Mémorise le choix sans modifier les autres réglages ni l'emplacement de la base."""
    config_path = user_data_destination() / "config" / "config.json"
    if not config_path.exists():
        return
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        profiles = config.get("profiles") or []
        active_id = config.get("active_profile_id")
        profile = next((item for item in profiles if item.get("id") == active_id), profiles[0] if profiles else None)
        if not profile:
            return
        profile["shortcut_icon"] = normalize_shortcut_icon(icon_key)
        temporary = config_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(config_path)
    except (OSError, ValueError, TypeError) as exc:
        log_installation(f"Choix d'icône non mémorisé : {exc}")


def running_application_process_ids(executable: Path) -> list[int]:
    if os.name != "nt" or not executable.exists():
        return []
    script = """
$Target = [IO.Path]::GetFullPath($env:EASY_CESU_EXE)
Get-Process -Name 'Easy CESU' -ErrorAction SilentlyContinue |
    Where-Object { $_.Path -and [String]::Equals([IO.Path]::GetFullPath($_.Path), $Target, [StringComparison]::OrdinalIgnoreCase) } |
    Select-Object -ExpandProperty Id
"""
    env = os.environ.copy()
    env["EASY_CESU_EXE"] = str(executable)
    completed = subprocess.run(
        [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return [int(value) for value in completed.stdout.splitlines() if value.strip().isdigit()]


def request_graceful_shutdown(executable: Path) -> bool:
    # On vérifie l'identité du serveur local avant d'envoyer une commande d'arrêt.
    expected_executable = executable.resolve(strict=False)
    process_ids = running_application_process_ids(executable)
    if not process_ids:
        return False
    script = """
$Ids = $env:EASY_CESU_PIDS -split ',' | ForEach-Object { [int]$_ }
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
    Where-Object { $_.OwningProcess -in $Ids } |
    Select-Object -ExpandProperty LocalPort -Unique
"""
    completed = subprocess.run(
        [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        env={**os.environ, "EASY_CESU_PIDS": ",".join(str(value) for value in process_ids)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    ports = [int(value) for value in completed.stdout.splitlines() if value.strip().isdigit()]
    for port in ports:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/app-info", timeout=0.5) as response:
                app_info = json.loads(response.read().decode("utf-8"))
            server_executable = Path(str(app_info.get("executable") or "")).resolve(strict=False)
            if app_info.get("app_name") != APP_NAME or server_executable != expected_executable:
                continue
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/api/shutdown",
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=2) as response:
                response.read()
            return True
        except Exception:
            continue
    return False


def wait_for_application_exit(executable: Path, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not running_application_process_ids(executable):
            return True
        time.sleep(0.2)
    return not running_application_process_ids(executable)


def force_stop_application(executable: Path) -> None:
    process_ids = running_application_process_ids(executable)
    if not process_ids:
        return
    subprocess.run(
        [
            powershell_executable(),
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            "Stop-Process -Id ($env:EASY_CESU_PIDS -split ',') -Force -ErrorAction SilentlyContinue",
        ],
        env={**os.environ, "EASY_CESU_PIDS": ",".join(str(value) for value in process_ids)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def stop_running_application(destination: Path) -> bool:
    # Une mise à jour doit libérer l'exécutable avant de remplacer les fichiers installés.
    executable = destination / EXE_NAME
    if not running_application_process_ids(executable):
        return False
    graceful_requested = request_graceful_shutdown(executable)
    if not graceful_requested:
        force_stop_application(executable)
    elif not wait_for_application_exit(executable, 6.0):
        force_stop_application(executable)
    if not wait_for_application_exit(executable, 5.0):
        raise RuntimeError(
            "Easy CESU est encore ouvert. Ferme l'application puis relance l'installation."
        )
    time.sleep(0.4)
    return True


def copy_file_with_retry(source: Path, target: Path) -> None:
    # Windows peut garder un fichier verrouillé quelques instants après l'arrêt du processus.
    for attempt in range(6):
        try:
            shutil.copy2(source, target)
            return
        except OSError as exc:
            if attempt == 5:
                raise RuntimeError(
                    f"Impossible de remplacer le fichier {target.name}. Ferme Easy CESU puis réessaie."
                ) from exc
            time.sleep(0.4)


def copy_payload(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Dossier application introuvable : {source}")
    has_existing_data = destination.exists()
    destination.mkdir(parents=True, exist_ok=True)
    for item in source.rglob("*"):
        rel = item.relative_to(source)
        if has_existing_data and should_preserve_existing(rel, destination):
            continue
        target = destination / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            copy_file_with_retry(item, target)


def remove_tree_with_retry(path: Path) -> None:
    for attempt in range(6):
        try:
            shutil.rmtree(path)
            return
        except FileNotFoundError:
            return
        except OSError as exc:
            if attempt == 5:
                raise RuntimeError(
                    f"Impossible de remplacer l'ancien moteur installé dans {path}."
                ) from exc
            time.sleep(0.4)


def replace_application_payload(source: Path, destination: Path) -> None:
    """Prépare la nouvelle version à part, puis remplace rapidement son moteur."""

    if not source.exists():
        raise FileNotFoundError(f"Dossier application introuvable : {source}")

    destination_parent = destination.parent
    destination_parent.mkdir(parents=True, exist_ok=True)
    staging = destination_parent / (
        f".{destination.name}.mise-a-jour-{os.getpid()}-{time.time_ns()}"
    )
    retired_runtime: Path | None = None

    try:
        log_installation("Préparation des fichiers de la nouvelle version")
        copy_payload(source, staging)
        staged_runtime = staging / "_internal"
        staged_executable = staging / EXE_NAME
        if not staged_runtime.is_dir() or not staged_executable.is_file():
            raise RuntimeError("Le paquet d'installation est incomplet.")

        destination.mkdir(parents=True, exist_ok=True)
        installed_runtime = destination / "_internal"
        if installed_runtime.exists():
            retired_runtime = destination / (
                f"_internal.precedente-{time.strftime('%Y%m%d%H%M%S')}-{os.getpid()}"
            )
            log_installation("Mise de côté de l'ancien moteur de l'application")
            installed_runtime.replace(retired_runtime)

        # Le déplacement reste sur le même disque et évite une longue copie
        # fichier par fichier au-dessus d'une version déjà installée.
        try:
            staged_runtime.replace(installed_runtime)
        except Exception:
            if retired_runtime and retired_runtime.exists() and not installed_runtime.exists():
                retired_runtime.replace(installed_runtime)
            raise
        copy_payload(staging, destination)
        log_installation("Fichiers de l'application remplacés")
    finally:
        if staging.exists():
            remove_tree_with_retry(staging)


def cleanup_retired_runtimes(destination: Path, timeout_seconds: float = 5.0) -> None:
    """Nettoie les anciens moteurs sans pouvoir bloquer la fin de l'installation."""

    for retired in destination.glob("_internal.precedente-*"):
        environment = os.environ.copy()
        environment["EASY_CESU_RETIRED_RUNTIME"] = str(retired)
        try:
            subprocess.run(
                [
                    powershell_executable(),
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-Command",
                    "Remove-Item -LiteralPath $env:EASY_CESU_RETIRED_RUNTIME -Recurse -Force -ErrorAction Stop",
                ],
                env=environment,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=timeout_seconds,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except subprocess.TimeoutExpired:
            log_installation(
                f"Nettoyage différé de l'ancienne version : {retired.name}"
            )


def remove_obsolete_notices(destination: Path) -> None:
    for notice in destination.glob("Easy_CESU_V*_Notice_Installation_et_Utilisation.pdf"):
        if notice.name != NOTICE_NAME:
            notice.unlink(missing_ok=True)


def migrate_legacy_data(destination: Path) -> None:
    local_appdata = Path(os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local"))
    for legacy_name in LEGACY_APP_NAMES:
        legacy = local_appdata / legacy_name
        if not legacy.exists() or legacy == destination:
            continue
        migrations = [
            (Path("config.json"), Path("config") / "config.json"),
            (Path("application") / "data", Path("data")),
        ]
        for source_rel, target_rel in migrations:
            source = legacy / source_rel
            target = destination / target_rel
            if not source.exists() or target.exists():
                continue
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)


def remove_obsolete_bundled_state(destination: Path) -> None:
    for rel in [Path("_internal") / "config.json", Path("_internal") / "application" / "data"]:
        target = destination / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def should_preserve_existing(rel: Path, destination: Path) -> bool:
    parts = rel.parts
    if rel == Path("config.json") and (destination / rel).exists():
        return True
    if len(parts) >= 2 and parts[0] == "application" and parts[1] == "data":
        return (destination / rel).exists()
    return False


def powershell_executable() -> str:
    windows_root = os.environ.get("SystemRoot") or os.environ.get("WINDIR") or r"C:\Windows"
    candidate = Path(windows_root) / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
    return str(candidate) if candidate.exists() else "powershell.exe"


def create_shortcut(shortcut_path: Path, target: Path, working_dir: Path, icon_path: Path | None = None) -> None:
    shortcut_path.parent.mkdir(parents=True, exist_ok=True)
    script = """
$ShortcutPath = $env:SHORTCUT_PATH
$TargetPath = $env:TARGET_PATH
$WorkingDirectory = $env:WORKING_DIRECTORY
$IconPath = $env:ICON_PATH
$Shell = New-Object -ComObject WScript.Shell
$Shortcut = $Shell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $WorkingDirectory
$Shortcut.IconLocation = if ($IconPath) { $IconPath } else { $TargetPath }
$Shortcut.Save()
"""
    env = os.environ.copy()
    env["SHORTCUT_PATH"] = str(shortcut_path)
    env["TARGET_PATH"] = str(target)
    env["WORKING_DIRECTORY"] = str(working_dir)
    env["ICON_PATH"] = str(icon_path or "")
    subprocess.run(
        [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )


def desktop_path() -> Path:
    try:
        completed = subprocess.run(
            [
                powershell_executable(),
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                "[Environment]::GetFolderPath('Desktop')",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        value = completed.stdout.strip()
        if value:
            return Path(value)
    except Exception:
        pass
    return Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"


def start_menu_path() -> Path:
    return start_menu_programs_path() / APP_NAME


def start_menu_programs_path() -> Path:
    appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"


def write_uninstall_script(destination: Path) -> None:
    uninstall = destination / "Desinstaller de ce PC.cmd"
    uninstall.write_text(
        "\n".join(
            [
                "@echo off",
                "setlocal",
                f'set "TARGET={destination}"',
                "for /f \"usebackq delims=\" %%D in (`powershell -NoProfile -Command \"[Environment]::GetFolderPath('Desktop')\"`) do set \"DESKTOP_DIR=%%D\"",
                f'if exist "%DESKTOP_DIR%\\{APP_NAME}.lnk" del "%DESKTOP_DIR%\\{APP_NAME}.lnk"',
                f'if exist "%USERPROFILE%\\Desktop\\{APP_NAME}.lnk" del "%USERPROFILE%\\Desktop\\{APP_NAME}.lnk"',
                f'del "%DESKTOP_DIR%\\{APP_NAME} V*.lnk" >nul 2>&1',
                f'del "%USERPROFILE%\\Desktop\\{APP_NAME} V*.lnk" >nul 2>&1',
                'if exist "%DESKTOP_DIR%\\Factures Cloclo.lnk" del "%DESKTOP_DIR%\\Factures Cloclo.lnk"',
                'if exist "%USERPROFILE%\\Desktop\\Factures Cloclo.lnk" del "%USERPROFILE%\\Desktop\\Factures Cloclo.lnk"',
                f'del "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_NAME}*.lnk" >nul 2>&1',
                f'if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_NAME}" rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\{APP_NAME}"',
                'if exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Factures Cloclo" rmdir /s /q "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Factures Cloclo"',
                f'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_ID}" /f >nul 2>&1',
                'if exist "%TARGET%" rmdir /s /q "%TARGET%"',
                "echo Application desinstallee.",
                "pause",
                "",
            ]
        ),
        encoding="ascii",
    )


def register_uninstall(destination: Path) -> None:
    """Inscrit l'installation pour que Windows puisse l'identifier durablement."""

    if os.name != "nt":
        return
    try:
        import winreg

        key_path = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_ID}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, APP_VERSION)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(destination))
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, str(destination / "Desinstaller de ce PC.cmd"))
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
    except OSError as exc:
        log_installation(f"Inscription Windows non disponible : {exc}")


def install(
    destination: Path,
    desktop_shortcut: bool,
    start_menu_shortcut: bool,
    open_notice: bool,
    launch_app: bool,
    shortcut_icon: str = "generique",
) -> dict:
    ensure_windows_x64()
    log_installation(f"Début installation {APP_VERSION} vers {destination}")
    webview2_version = ensure_webview2_runtime()
    log_installation(f"Microsoft WebView2 disponible : {webview2_version}")
    source = resource_root()
    closed_existing = stop_running_application(destination)
    log_installation("Application existante arrêtée")
    replace_application_payload(source, destination)
    remove_obsolete_bundled_state(destination)
    remove_obsolete_notices(destination)
    migrate_legacy_data(user_data_destination())
    exe = destination / EXE_NAME
    if not exe.exists():
        raise FileNotFoundError(f"Executable introuvable apres copie : {exe}")

    icon_key = normalize_shortcut_icon(shortcut_icon)
    installed_icon = install_shortcut_icon(destination, icon_key)
    remove_previous_easy_cesu_shortcuts()
    if desktop_shortcut:
        create_shortcut(desktop_path() / f"{shortcut_label()}.lnk", exe, destination, installed_icon)
    if start_menu_shortcut:
        create_shortcut(start_menu_path() / f"{shortcut_label()}.lnk", exe, destination, installed_icon)
    remove_legacy_shortcuts()
    write_uninstall_script(destination)
    register_uninstall(destination)
    remember_shortcut_icon(icon_key)
    cleanup_retired_runtimes(destination)

    notice = destination / NOTICE_NAME
    if open_notice and notice.exists():
        os.startfile(notice)  # type: ignore[attr-defined]
    if launch_app:
        subprocess.Popen([str(exe)], cwd=str(destination), close_fds=True)

    log_installation(f"Installation terminée vers {destination}")

    return {
        "destination": str(destination),
        "desktop_shortcut": desktop_shortcut,
        "start_menu_shortcut": start_menu_shortcut,
        "notice": str(notice) if notice.exists() else "",
        "launched": launch_app,
        "closed_existing": closed_existing,
        "shortcut_icon": icon_key,
        "webview2_version": webview2_version,
    }


def elevated_install_args(
    destination: Path,
    desktop_shortcut: bool,
    start_menu_shortcut: bool,
    open_notice: bool,
    launch_app: bool,
    shortcut_icon: str,
) -> tuple[str, list[str]]:
    install_args = [
        "--install",
        "--destination",
        str(destination),
        "--shortcut-icon",
        normalize_shortcut_icon(shortcut_icon),
    ]
    if desktop_shortcut:
        install_args.append("--desktop-shortcut")
    if start_menu_shortcut:
        install_args.append("--start-menu-shortcut")
    if open_notice:
        install_args.append("--open-notice")
    if launch_app:
        install_args.append("--launch")
    if getattr(sys, "frozen", False):
        return sys.executable, install_args
    return sys.executable, [str(Path(__file__).resolve()), *install_args]


def run_elevated_install(
    destination: Path,
    desktop_shortcut: bool,
    start_menu_shortcut: bool,
    open_notice: bool,
    launch_app: bool,
    shortcut_icon: str = "generique",
) -> dict:
    executable, args = elevated_install_args(
        destination,
        desktop_shortcut,
        start_menu_shortcut,
        open_notice,
        launch_app,
        shortcut_icon,
    )
    script = """
$Process = Start-Process -FilePath $env:EASY_CESU_INSTALLER_FILE -ArgumentList $env:EASY_CESU_INSTALLER_ARGS -Verb RunAs -Wait -PassThru
if ($null -eq $Process.ExitCode) { exit 0 }
exit $Process.ExitCode
"""
    env = os.environ.copy()
    env["EASY_CESU_INSTALLER_FILE"] = executable
    env["EASY_CESU_INSTALLER_ARGS"] = subprocess.list2cmdline(args)
    completed = subprocess.run(
        [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or "Installation annulee ou refusee par Windows."
        raise RuntimeError(message)
    return {
        "destination": str(destination),
        "desktop_shortcut": desktop_shortcut,
        "start_menu_shortcut": start_menu_shortcut,
        "elevated": True,
        "shortcut_icon": normalize_shortcut_icon(shortcut_icon),
    }


def remove_legacy_shortcuts() -> None:
    shortcut_dirs = [desktop_path(), Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop"]
    appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
    shortcut_dirs.append(Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs")
    for legacy_name in LEGACY_APP_NAMES:
        for folder in shortcut_dirs:
            shortcut = folder / f"{legacy_name}.lnk"
            if shortcut.exists():
                shortcut.unlink()
        start_folder = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / legacy_name
        if start_folder.exists():
            shutil.rmtree(start_folder)


def remove_previous_easy_cesu_shortcuts() -> None:
    """Ne conserve qu'un raccourci Easy CESU, portant la version active."""
    folders = [
        desktop_path(),
        Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Desktop",
        start_menu_path(),
        start_menu_programs_path(),
    ]
    for folder in folders:
        if not folder.exists():
            continue
        for shortcut in folder.glob(f"{APP_NAME}*.lnk"):
            try:
                shortcut.unlink()
            except OSError:
                pass


def run_post_install_actions(destination: Path, open_notice: bool, launch_app: bool) -> None:
    """Ouvre les éléments demandés seulement après la fermeture de l'installateur."""
    notice = destination / NOTICE_NAME
    executable = destination / EXE_NAME
    if open_notice and notice.exists():
        try:
            os.startfile(notice)  # type: ignore[attr-defined]
        except OSError as exc:
            log_installation(f"Ouverture de la notice impossible : {exc}")
    if launch_app and executable.exists():
        try:
            subprocess.Popen([str(executable)], cwd=str(destination), close_fds=True)
        except OSError as exc:
            log_installation(f"Lancement de l'application impossible : {exc}")


class InstallerWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"Installation - {APP_NAME}")
        self.resizable(False, False)
        icon_path = installer_icon_path()
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except tk.TclError:
                # Une icone indisponible ne doit jamais bloquer l'installation.
                pass
        self.destination = tk.StringVar(value=str(default_destination()))
        self.desktop_shortcut = tk.BooleanVar(value=True)
        self.start_menu_shortcut = tk.BooleanVar(value=True)
        self.open_notice = tk.BooleanVar(value=True)
        self.launch_app = tk.BooleanVar(value=True)
        initial_icon = configured_shortcut_icon()
        self.shortcut_icon_label = tk.StringVar(value=SHORTCUT_ICON_LABELS[initial_icon])
        self.shortcut_icon_preview: tk.PhotoImage | None = None
        self.status = tk.StringVar(value="")
        self.build()

    def build(self) -> None:
        frame = ttk.Frame(self, padding=18)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text=APP_NAME, font=("Segoe UI", 15, "bold")).grid(row=0, column=0, columnspan=3, sticky="w")
        ttk.Label(frame, text="Choisis le dossier d'installation et les raccourcis a creer.").grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(4, 16)
        )

        ttk.Label(frame, text="Dossier d'installation").grid(row=2, column=0, columnspan=3, sticky="w")
        entry = ttk.Entry(frame, width=62, textvariable=self.destination)
        entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 10))
        ttk.Button(frame, text="Parcourir", command=self.choose_destination).grid(row=3, column=2, padx=(8, 0), pady=(4, 10))

        ttk.Label(frame, text="Icône du raccourci").grid(row=4, column=0, columnspan=2, sticky="w")
        icon_select = ttk.Combobox(
            frame,
            width=48,
            state="readonly",
            values=list(SHORTCUT_ICON_LABELS.values()),
            textvariable=self.shortcut_icon_label,
        )
        icon_select.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 10))
        icon_select.bind("<<ComboboxSelected>>", lambda _event: self.update_shortcut_icon_preview())
        self.icon_preview_label = ttk.Label(frame)
        self.icon_preview_label.grid(row=4, column=2, rowspan=2, padx=(12, 0), sticky="e")
        self.update_shortcut_icon_preview()

        ttk.Checkbutton(frame, text="Creer un raccourci sur le Bureau", variable=self.desktop_shortcut).grid(
            row=6, column=0, columnspan=3, sticky="w"
        )
        ttk.Checkbutton(frame, text="Creer un raccourci dans le menu Demarrer", variable=self.start_menu_shortcut).grid(
            row=7, column=0, columnspan=3, sticky="w"
        )
        ttk.Checkbutton(frame, text="Ouvrir la notice a la fin", variable=self.open_notice).grid(
            row=8, column=0, columnspan=3, sticky="w"
        )
        ttk.Checkbutton(frame, text="Lancer l'application apres l'installation", variable=self.launch_app).grid(
            row=9, column=0, columnspan=3, sticky="w"
        )

        ttk.Label(frame, textvariable=self.status).grid(row=10, column=0, columnspan=3, sticky="w", pady=(14, 4))
        self.install_button = ttk.Button(frame, text="Installer", command=self.run_install)
        self.install_button.grid(row=11, column=1, sticky="e", pady=(10, 0))
        self.cancel_button = ttk.Button(frame, text="Annuler", command=self.destroy)
        self.cancel_button.grid(row=11, column=2, sticky="e", padx=(8, 0), pady=(10, 0))

    def selected_shortcut_icon(self) -> str:
        selected_label = self.shortcut_icon_label.get()
        return next(
            (key for key, label in SHORTCUT_ICON_LABELS.items() if label == selected_label),
            "generique",
        )

    def update_shortcut_icon_preview(self) -> None:
        preview_path = shortcut_icon_preview_path(self.selected_shortcut_icon())
        if not preview_path.exists():
            self.icon_preview_label.configure(image="")
            self.shortcut_icon_preview = None
            return
        try:
            self.shortcut_icon_preview = tk.PhotoImage(file=str(preview_path))
            self.icon_preview_label.configure(image=self.shortcut_icon_preview)
        except tk.TclError:
            self.icon_preview_label.configure(image="")
            self.shortcut_icon_preview = None

    def choose_destination(self) -> None:
        selected = filedialog.askdirectory(initialdir=str(Path(self.destination.get()).parent), title="Dossier d'installation")
        if selected:
            self.destination.set(str(Path(selected) / APP_NAME if Path(selected).name != APP_NAME else Path(selected)))

    def resolve_destination_choice(self, destination: Path) -> Path | None:
        existing = detect_existing_installations(destination)
        if not existing:
            return destination

        replacement = choose_replacement_target(destination, existing)
        additional = unique_install_destination(destination)
        installed_list = "\n".join(f"- {path}" for path in existing)
        answer = messagebox.askyesnocancel(
            APP_NAME,
            "Une version de Easy CESU est déjà installée :\n\n"
            f"{installed_list}\n\n"
            "Oui : remplacer / mettre à jour la version existante.\n"
            f"Non : installer une copie en plus dans :\n{additional}\n"
            "Annuler : ne rien installer.",
        )
        if answer is None:
            return None
        if answer is False:
            self.destination.set(str(additional))
            return additional
        self.destination.set(str(replacement))
        return replacement

    def run_install(self) -> None:
        try:
            destination = Path(self.destination.get()).expanduser()
            destination = self.resolve_destination_choice(destination)
            if destination is None:
                self.status.set("")
                return
            self.status.set("Installation en cours...")
            self.install_button.configure(state="disabled")
            self.cancel_button.configure(state="disabled")
            open_notice = self.open_notice.get()
            launch_app = self.launch_app.get()
            desktop_shortcut = self.desktop_shortcut.get()
            start_menu_shortcut = self.start_menu_shortcut.get()
            shortcut_icon = self.selected_shortcut_icon()
            elevated = requires_elevation(destination) and not is_admin()
            if elevated:
                answer = messagebox.askyesno(
                    APP_NAME,
                    "Ce dossier demande une autorisation Windows.\n\n"
                    "Clique sur Oui pour continuer l'installation en mode administrateur.",
                )
                if not answer:
                    self.status.set("")
                    self.install_button.configure(state="normal")
                    self.cancel_button.configure(state="normal")
                    return
            threading.Thread(
                target=self._install_worker,
                args=(destination, desktop_shortcut, start_menu_shortcut, open_notice, launch_app, shortcut_icon, elevated),
                name="easy-cesu-installer",
                daemon=False,
            ).start()
        except Exception as exc:  # noqa: BLE001
            self.status.set("")
            self.install_button.configure(state="normal")
            self.cancel_button.configure(state="normal")
            messagebox.showerror(APP_NAME, str(exc))

    def _install_worker(
        self,
        destination: Path,
        desktop_shortcut: bool,
        start_menu_shortcut: bool,
        open_notice: bool,
        launch_app: bool,
        shortcut_icon: str,
        elevated: bool,
    ) -> None:
        try:
            if elevated:
                result = run_elevated_install(
                    destination,
                    desktop_shortcut,
                    start_menu_shortcut,
                    False,
                    False,
                    shortcut_icon,
                )
            else:
                result = install(
                    destination,
                    desktop_shortcut,
                    start_menu_shortcut,
                    False,
                    False,
                    shortcut_icon,
                )
            self.after(0, self._finish_install, result, open_notice, launch_app)
        except Exception as exc:  # noqa: BLE001
            self.after(0, self._show_install_error, str(exc))

    def _finish_install(self, result: dict, open_notice: bool, launch_app: bool) -> None:
        destination = Path(result["destination"])
        self.withdraw()
        self.destroy()
        run_post_install_actions(destination, open_notice, launch_app)

    def _show_install_error(self, message: str) -> None:
        self.status.set("")
        self.install_button.configure(state="normal")
        self.cancel_button.configure(state="normal")
        messagebox.showerror(APP_NAME, message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=f"Installateur Windows pour {APP_NAME}.")
    parser.add_argument("--install", action="store_true", help="Installe sans afficher la fenetre.")
    parser.add_argument("--destination", default=str(default_destination()), help="Dossier d'installation.")
    parser.add_argument("--desktop-shortcut", action="store_true", help="Cree un raccourci Bureau.")
    parser.add_argument("--start-menu-shortcut", action="store_true", help="Cree un raccourci menu Demarrer.")
    parser.add_argument(
        "--shortcut-icon",
        choices=tuple(SHORTCUT_ICON_LABELS),
        default=configured_shortcut_icon(),
        help="Icone metier utilisee par les raccourcis.",
    )
    parser.add_argument("--open-notice", action="store_true", help="Ouvre la notice apres installation.")
    parser.add_argument("--launch", action="store_true", help="Lance l'application apres installation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.install:
        destination = Path(args.destination).expanduser()
        if requires_elevation(destination) and not is_admin():
            result = run_elevated_install(
                destination,
                args.desktop_shortcut,
                args.start_menu_shortcut,
                args.open_notice,
                args.launch,
                args.shortcut_icon,
            )
        else:
            result = install(
                destination,
                args.desktop_shortcut,
                args.start_menu_shortcut,
                args.open_notice,
                args.launch,
                args.shortcut_icon,
            )
        print(json.dumps(result, ensure_ascii=False))
        return 0
    InstallerWindow().mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
