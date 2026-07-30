from __future__ import annotations

import re
import smtplib
import ssl
from contextlib import contextmanager
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path
from typing import Iterator

try:
    import keyring
    from keyring.errors import KeyringError, PasswordDeleteError
except ImportError:  # pragma: no cover - dépendance incluse dans les applications distribuées
    keyring = None

    class KeyringError(Exception):
        pass

    class PasswordDeleteError(KeyringError):
        pass


SMTP_SECURITY_MODES = {"starttls", "ssl", "none"}
EMAIL_TEMPLATE_FIELDS = {
    "client",
    "mois",
    "annee",
    "heures",
    "montant",
    "nom",
}
DEFAULT_EMAIL_SUBJECT = "Note d'intervention - {mois} {annee} - {client}"
DEFAULT_EMAIL_BODY = """Bonjour,

Veuillez trouver en pièce jointe votre note d'intervention pour {mois} {annee}.

Nombre d'heures : {heures}
Montant net : {montant}

Cordialement,
{nom}"""
KEYRING_SERVICE = "Easy CESU SMTP"
TEMPLATE_FIELD_PATTERN = re.compile(r"\{([a-z_]+)\}")


def smtp_defaults() -> dict:
    return {
        "smtp_host": "",
        "smtp_port": 587,
        "smtp_security": "starttls",
        "smtp_username": "",
        "smtp_sender_name": "",
        "smtp_sender_email": "",
        "email_subject_template": DEFAULT_EMAIL_SUBJECT,
        "email_body_template": DEFAULT_EMAIL_BODY,
    }


def normalize_smtp_settings(settings: dict, *, require_complete: bool = False) -> dict:
    normalized = smtp_defaults()
    for field in normalized:
        if field in settings and settings[field] is not None:
            normalized[field] = settings[field]
    normalized["smtp_host"] = str(normalized["smtp_host"] or "").strip()
    normalized["smtp_username"] = str(normalized["smtp_username"] or "").strip()
    normalized["smtp_sender_name"] = str(normalized["smtp_sender_name"] or "").strip()
    normalized["smtp_sender_email"] = str(normalized["smtp_sender_email"] or "").strip()
    normalized["email_subject_template"] = str(normalized["email_subject_template"] or "").strip()
    normalized["email_body_template"] = str(normalized["email_body_template"] or "").strip()
    try:
        normalized["smtp_port"] = int(normalized["smtp_port"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Port SMTP invalide.") from exc
    if not 1 <= normalized["smtp_port"] <= 65535:
        raise ValueError("Le port SMTP doit être compris entre 1 et 65535.")
    normalized["smtp_security"] = str(normalized["smtp_security"] or "").strip().lower()
    if normalized["smtp_security"] not in SMTP_SECURITY_MODES:
        raise ValueError("Mode de sécurité SMTP inconnu.")
    if normalized["smtp_sender_email"] and "@" not in normalized["smtp_sender_email"]:
        raise ValueError("Adresse d'expédition invalide.")
    if require_complete:
        if not normalized["smtp_host"]:
            raise ValueError("Renseigne le serveur SMTP dans les réglages.")
        if not normalized["smtp_sender_email"]:
            raise ValueError("Renseigne l'adresse d'expédition dans les réglages.")
        if not normalized["email_subject_template"]:
            raise ValueError("Renseigne l'objet du modèle de mail.")
        if not normalized["email_body_template"]:
            raise ValueError("Renseigne le texte du modèle de mail.")
    for field in ("email_subject_template", "email_body_template"):
        unknown = set(TEMPLATE_FIELD_PATTERN.findall(normalized[field])) - EMAIL_TEMPLATE_FIELDS
        if unknown:
            names = ", ".join(sorted(f"{{{name}}}" for name in unknown))
            raise ValueError(f"Champ inconnu dans le modèle de mail : {names}.")
    return normalized


def render_email_template(template: str, values: dict[str, str]) -> str:
    return TEMPLATE_FIELD_PATTERN.sub(
        lambda match: values.get(match.group(1), match.group(0)),
        template,
    )


def password_saved(profile_id: str) -> bool:
    return bool(get_smtp_password(profile_id))


def get_smtp_password(profile_id: str) -> str:
    if keyring is None:
        return ""
    try:
        return str(keyring.get_password(KEYRING_SERVICE, profile_id) or "")
    except KeyringError:
        return ""


def save_smtp_password(profile_id: str, password: str) -> None:
    if keyring is None:
        raise ValueError("Le coffre de mots de passe du système n'est pas disponible.")
    try:
        keyring.set_password(KEYRING_SERVICE, profile_id, password)
    except KeyringError as exc:
        raise ValueError("Impossible d'enregistrer le mot de passe dans le coffre du système.") from exc


def delete_smtp_password(profile_id: str) -> None:
    if keyring is None:
        return
    try:
        keyring.delete_password(KEYRING_SERVICE, profile_id)
    except (KeyringError, PasswordDeleteError):
        return


@contextmanager
def smtp_connection(settings: dict, password: str, timeout: float = 20.0) -> Iterator[smtplib.SMTP]:
    config = normalize_smtp_settings(settings, require_complete=True)
    server: smtplib.SMTP | None = None
    try:
        if config["smtp_security"] == "ssl":
            server = smtplib.SMTP_SSL(
                config["smtp_host"],
                config["smtp_port"],
                timeout=timeout,
                context=ssl.create_default_context(),
            )
        else:
            server = smtplib.SMTP(config["smtp_host"], config["smtp_port"], timeout=timeout)
            server.ehlo()
            if config["smtp_security"] == "starttls":
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
        if config["smtp_username"]:
            if not password:
                raise ValueError("Renseigne le mot de passe SMTP dans les réglages.")
            server.login(config["smtp_username"], password)
        yield server
    except smtplib.SMTPAuthenticationError as exc:
        raise ValueError("Authentification refusée. Vérifie l'identifiant et le mot de passe d'application.") from exc
    except (OSError, smtplib.SMTPException) as exc:
        raise ValueError(f"Connexion au serveur SMTP impossible : {exc}") from exc
    finally:
        if server is not None:
            try:
                server.quit()
            except (OSError, smtplib.SMTPException):
                try:
                    server.close()
                except OSError:
                    pass


def build_email_message(
    settings: dict,
    recipient: str,
    subject: str,
    body: str,
    attachment: Path,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = formataddr((settings["smtp_sender_name"], settings["smtp_sender_email"]))
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    message.add_attachment(
        attachment.read_bytes(),
        maintype="application",
        subtype="pdf",
        filename=attachment.name,
    )
    return message
