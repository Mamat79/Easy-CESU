"""Lance une instance de contrôle visuel sans toucher aux données installées."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "tmp" / "email-ui-data-v315"
os.environ["EASY_CESU_DATA_ROOT"] = str(DATA_ROOT)
os.environ["NOTES_APP_PORT"] = os.environ.get("NOTES_APP_PORT", "8875")
sys.frozen = True
sys._MEIPASS = str(ROOT)
sys.path.insert(0, str(ROOT / "application"))
sys.path.insert(0, str(ROOT))

import app_server  # noqa: E402


def seed() -> None:
    app_server.init_db()
    with app_server.db_connection() as database:
        database.execute("DELETE FROM contract_terminations")
        database.execute("DELETE FROM interventions")
        database.execute("DELETE FROM clients")
    intervention_ids: dict[str, int] = {}
    for index, (name, email, enabled, review) in enumerate((
        ("Mme Martin", "martin@example.test", True, False),
        ("M. Dupont", "dupont@example.test", True, True),
        ("Mme Bernard", "", False, False),
    )):
        app_server.create_client(
            {
                "name": name,
                "email": email,
                "email_notes_enabled": enabled,
                "email_review_before_send": review,
            }
        )
        intervention = app_server.create_intervention(
            {
                "date": f"2026-07-{12 + index:02d}",
                "client": name,
                "duration_hours": 1.5 + index * 0.5,
                "hourly_rate": 22,
                "task": "Prestation de démonstration",
            }
        )
        intervention_ids[name] = int(intervention["id"])

    app_server.create_client({"name": "M. Ancien", "email": "ancien@example.test"})
    archived_intervention = app_server.create_intervention(
        {
            "date": "2024-05-10",
            "client": "M. Ancien",
            "duration_hours": 2,
            "hourly_rate": 20,
            "task": "Intervention historique",
        }
    )
    for reminder_type in ("transmitted", "declared", "paid"):
        app_server.update_intervention_administrative_status(archived_intervention["id"], reminder_type, True)
    app_server.set_client_archived("M. Ancien", True)

    # Trois situations distinctes permettent de contrôler le tableau sans
    # utiliser la base personnelle : tout à faire, déclaration seule, terminé.
    for reminder_type in ("transmitted", "paid"):
        app_server.update_intervention_administrative_status(intervention_ids["M. Dupont"], reminder_type, True)
    for reminder_type in ("transmitted", "declared", "paid"):
        app_server.update_intervention_administrative_status(intervention_ids["Mme Bernard"], reminder_type, True)
    profile = app_server.active_profile()
    profile.update(
        {
            "smtp_host": "smtp.example.test",
            "smtp_port": 587,
            "smtp_security": "starttls",
            "smtp_username": "",
            "smtp_sender_name": "Compte de démonstration",
            "smtp_sender_email": "demo@example.test",
        }
    )
    app_server.CONFIG["initial_setup_completed"] = True
    app_server.save_config()


if __name__ == "__main__":
    seed()
    raise SystemExit(app_server.main(open_browser=False))
