"""Archives ZIP de transfert Easy CESU, avec vérification avant restauration."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath


BACKUP_FORMAT = "easy-cesu-backup"
BACKUP_VERSION = 1
MAX_ARCHIVE_FILES = 2_000
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 512 * 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sqlite_snapshot(source: Path, target: Path) -> None:
    """Produit une image SQLite cohérente, même si l'application est ouverte."""

    target.parent.mkdir(parents=True, exist_ok=True)
    input_db = sqlite3.connect(f"file:{source}?mode=ro", uri=True)
    output_db = sqlite3.connect(target)
    try:
        input_db.backup(output_db)
    finally:
        output_db.close()
        input_db.close()
    check = sqlite3.connect(target)
    try:
        if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("La copie de la base SQLite est invalide.")
    finally:
        check.close()


def _safe_archive_path(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or path.parts[0] in {"", "."}:
        raise ValueError("L'archive contient un chemin non autorisé.")
    return path


def create_backup(
    output_path: Path,
    database_path: Path,
    config: dict,
    profile_id: str,
    attachments_dir: Path | None = None,
) -> dict:
    """Crée une archive autonome contenant la base, le profil et les pièces jointes."""

    if not database_path.exists():
        raise ValueError("Base de données introuvable pour la sauvegarde.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="easycesu-backup-") as raw_temp:
        temp = Path(raw_temp)
        snapshot = temp / "database.sqlite"
        sqlite_snapshot(database_path, snapshot)
        profile_config = temp / "profile.json"
        profile_config.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        files = [(snapshot, "database.sqlite"), (profile_config, "profile.json")]
        if attachments_dir and attachments_dir.exists():
            for source in attachments_dir.rglob("*"):
                if source.is_file():
                    files.append((source, f"attachments/{source.relative_to(attachments_dir).as_posix()}"))
        manifest_files = []
        for source, archive_name in files:
            manifest_files.append(
                {"path": archive_name, "size": source.stat().st_size, "sha256": sha256_file(source)}
            )
        manifest = {
            "format": BACKUP_FORMAT,
            "version": BACKUP_VERSION,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "profile_id": profile_id,
            "files": manifest_files,
        }
        temp_manifest = temp / "manifest.json"
        temp_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        target_temp = output_path.with_suffix(output_path.suffix + ".tmp")
        with zipfile.ZipFile(target_temp, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(temp_manifest, "manifest.json")
            for source, archive_name in files:
                archive.write(source, archive_name)
        os.replace(target_temp, output_path)
    return {"path": str(output_path), "manifest": manifest}


def verify_backup(archive_path: Path) -> dict:
    """Contrôle le manifeste, les empreintes, la base et les chemins avant toute écriture."""

    if not archive_path.exists() or not archive_path.is_file():
        raise ValueError("Archive de sauvegarde introuvable.")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_FILES:
                raise ValueError("Archive trop volumineuse en nombre de fichiers.")
            if sum(item.file_size for item in infos) > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise ValueError("Archive trop volumineuse.")
            for info in infos:
                _safe_archive_path(info.filename)
                if info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError("Archive contenant un type de fichier non autorisé.")
            try:
                manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            except (KeyError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ValueError("Manifeste de sauvegarde invalide.") from exc
            if manifest.get("format") != BACKUP_FORMAT or manifest.get("version") != BACKUP_VERSION:
                raise ValueError("Format de sauvegarde Easy CESU non reconnu.")
            files = manifest.get("files")
            if not isinstance(files, list) or not files:
                raise ValueError("Manifeste de sauvegarde incomplet.")
            declared = set()
            for item in files:
                name = str(item.get("path") or "")
                _safe_archive_path(name)
                if name in declared:
                    raise ValueError("Manifeste de sauvegarde dupliqué.")
                declared.add(name)
                data = archive.read(name)
                if len(data) != int(item.get("size", -1)):
                    raise ValueError(f"Taille invalide pour {name}.")
                if hashlib.sha256(data).hexdigest() != item.get("sha256"):
                    raise ValueError(f"Empreinte invalide pour {name}.")
            if "database.sqlite" not in declared or "profile.json" not in declared:
                raise ValueError("La sauvegarde ne contient pas les données indispensables.")
            with tempfile.TemporaryDirectory(prefix="easycesu-verify-") as raw_temp:
                database = Path(raw_temp) / "database.sqlite"
                database.write_bytes(archive.read("database.sqlite"))
                check = sqlite3.connect(database)
                try:
                    if check.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                        raise ValueError("La base contenue dans l'archive est invalide.")
                finally:
                    check.close()
                profile = json.loads(archive.read("profile.json").decode("utf-8"))
                if not isinstance(profile, dict):
                    raise ValueError("Profil de sauvegarde invalide.")
    except zipfile.BadZipFile as exc:
        raise ValueError("Le fichier choisi n'est pas une archive ZIP valide.") from exc
    return {"manifest": manifest, "profile": profile}


def extract_backup_from_transfer_kit(archive_path: Path, destination: Path) -> Path:
    """Récupère la sauvegarde incluse dans le ZIP de transfert Easy CESU."""

    if not archive_path.exists() or not archive_path.is_file():
        raise ValueError("Archive de sauvegarde introuvable.")
    try:
        with zipfile.ZipFile(archive_path) as archive:
            infos = archive.infolist()
            if len(infos) > MAX_ARCHIVE_FILES:
                raise ValueError("Archive trop volumineuse en nombre de fichiers.")
            if sum(item.file_size for item in infos) > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise ValueError("Archive trop volumineuse.")
            candidates = []
            for info in infos:
                path = _safe_archive_path(info.filename)
                if info.is_dir() or (info.external_attr >> 16) & 0o170000 == 0o120000:
                    continue
                if path.name.lower().startswith("sauvegarde_easycesu_") and path.suffix.lower() == ".zip":
                    candidates.append(info)
            if len(candidates) != 1:
                raise ValueError("Le ZIP de transfert doit contenir une seule sauvegarde Easy CESU.")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(candidates[0]) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
    except zipfile.BadZipFile as exc:
        raise ValueError("Le fichier choisi n'est pas une archive ZIP valide.") from exc

    verify_backup(destination)
    return destination


def extract_backup(archive_path: Path, destination: Path) -> dict:
    """Extrait une archive préalablement validée dans un répertoire temporaire."""

    details = verify_backup(archive_path)
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        for item in details["manifest"]["files"]:
            name = str(item["path"])
            target = destination.joinpath(*PurePosixPath(name).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(archive.read(name))
    return details
