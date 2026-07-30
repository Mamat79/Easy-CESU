"""Lance une instance de contrôle visuel sans toucher aux données installées."""

from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "tmp" / "email-ui-data-v313"
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
        database.execute("DELETE FROM interventions")
        database.execute("DELETE FROM clients")
    for name, email, enabled, review in (
        ("Mme Martin", "martin@example.test", True, False),
        ("M. Dupont", "dupont@example.test", True, True),
        ("Mme Bernard", "", False, False),
    ):
        app_server.create_client(
            {
                "name": name,
                "email": email,
                "email_notes_enabled": enabled,
                "email_review_before_send": review,
            }
        )
        app_server.create_intervention(
            {
                "date": "2026-07-12",
                "client": name,
                "duration_hours": 1.5,
                "hourly_rate": 22,
            }
        )
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
