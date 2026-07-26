from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYTHON = Path(sys.executable)


class AppServerIsolatedTests(unittest.TestCase):
    def run_scenario(self, scenario: str) -> None:
        with tempfile.TemporaryDirectory(prefix="easy-cesu-tests-") as temporary:
            temporary_path = Path(temporary)
            local_app_data = temporary_path / "local-app-data"
            resource_dir = temporary_path / "resources"
            workspace_dir = temporary_path / "workspace"
            local_app_data.mkdir()
            resource_dir.mkdir()

            bootstrap = f"""import os
import sys
from pathlib import Path

project = Path(r"{PROJECT_ROOT}")
os.environ["LOCALAPPDATA"] = r"{local_app_data}"
sys.frozen = True
sys._MEIPASS = r"{resource_dir}"
sys.executable = str(Path(os.environ["LOCALAPPDATA"]) / "Easy CESU.exe")
sys.path.insert(0, str(project / "application"))
sys.path.insert(0, str(project))

import app_server
"""
            script = bootstrap + "\n" + textwrap.dedent(scenario)
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["EASY_CESU_TEST_WORKSPACE"] = str(workspace_dir)
            completed = subprocess.run(
                [str(PYTHON), "-c", script],
                cwd=PROJECT_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_new_install_uses_generic_profile_and_workspace(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            settings = app_server.app_settings()
            assert settings["initial_setup_required"] is True
            assert settings["profile"]["label"] == "Mon compte"

            configured = app_server.configure_workspace_root(Path(os.environ["EASY_CESU_TEST_WORKSPACE"]))
            assert Path(configured["data_dir"]).is_dir()
            assert Path(configured["notes_intervention_dir"]).is_dir()
            assert Path(configured["export_dir"]).is_dir()
            assert app_server.app_settings()["initial_setup_required"] is False
            """
        )

    def test_client_creation_and_renaming_keeps_interventions(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_client({"name": "Client Test", "phone": "0600000000"})
            intervention = app_server.create_intervention(
                {"date": "2026-07-12", "client": "Client Test", "duration_hours": 2, "hourly_rate": 22}
            )
            updated = app_server.update_client("Client Test", {"name": "Client Renomme", "phone": "0600000000"})
            assert updated["name"] == "Client Renomme"
            rows = app_server.list_interventions(2026, 7)
            assert rows[0]["id"] == intervention["id"]
            assert rows[0]["client"] == "Client Renomme"
            """
        )

    def test_custom_rate_is_used_and_invalid_duration_is_rejected(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_client({"name": "Client Tarif", "hourly_rate": 24.5, "hourly_rate_custom": True})
            intervention = app_server.create_intervention(
                {"date": "2026-07-12", "client": "Client Tarif", "duration_hours": 1.5, "hourly_rate": 22}
            )
            assert intervention["hourly_rate"] == 24.5
            assert intervention["amount_net"] == 36.75
            _, error = app_server.validate_intervention(
                {"date": "2026-07-12", "client": "Client Tarif", "duration_hours": 0, "hourly_rate": 22}
            )
            assert error == "La durée doit être supérieure à zéro."
            """
        )

    def test_database_backup_is_readable(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_intervention(
                {"date": "2026-07-12", "client": "Client Sauvegarde", "duration_hours": 1, "hourly_rate": 22}
            )
            backup = app_server.backup_database_to(Path(os.environ["EASY_CESU_TEST_WORKSPACE"]))
            path = Path(backup["backup"])
            assert path.exists()
            import sqlite3
            with sqlite3.connect(path) as database:
                assert database.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
                assert database.execute("SELECT COUNT(*) FROM interventions").fetchone()[0] == 1
            """
        )

    def test_inaccessible_client_source_does_not_block_startup(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            source_dir = Path(os.environ["EASY_CESU_TEST_WORKSPACE"])
            source_dir.mkdir(parents=True, exist_ok=True)
            source_file = source_dir / "Suivi de paye 2026.xlsx"
            source_file.write_text("source volontairement inaccessible", encoding="utf-8")
            app_server.active_profile()["suivi_paye_dir"] = str(source_dir)
            app_server.save_config()
            original_loader = app_server.load_workbook
            app_server.load_workbook = lambda *args, **kwargs: (_ for _ in ()).throw(PermissionError("Accès refusé"))
            try:
                app_server.init_db()
            finally:
                app_server.load_workbook = original_loader
            assert app_server.clients_list() == []
            """
        )

    def test_v2_migration_preserves_existing_interventions(self) -> None:
        self.run_scenario(
            """
            import sqlite3
            database_path = app_server.active_db_path()
            database_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(database_path) as db:
                db.executescript(
                    '''
                    CREATE TABLE clients (
                        name TEXT PRIMARY KEY,
                        cesu TEXT NOT NULL DEFAULT '',
                        email TEXT NOT NULL DEFAULT '',
                        hourly_rate REAL NOT NULL DEFAULT 0,
                        hourly_rate_custom INTEGER NOT NULL DEFAULT 0,
                        address TEXT NOT NULL DEFAULT '',
                        phone TEXT NOT NULL DEFAULT '',
                        updated_at TEXT NOT NULL
                    );
                    CREATE TABLE interventions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        client TEXT NOT NULL,
                        duration_hours REAL NOT NULL,
                        hourly_rate REAL NOT NULL,
                        task TEXT NOT NULL DEFAULT '',
                        location TEXT NOT NULL DEFAULT '',
                        transmitted INTEGER NOT NULL DEFAULT 0,
                        paid INTEGER NOT NULL DEFAULT 0,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );
                    '''
                )
                db.execute("INSERT INTO clients VALUES (?, '', '', 22, 0, '', '', ?)", ("Client historique", "2026-01-01T10:00:00"))
                db.execute(
                    "INSERT INTO interventions (date, client, duration_hours, hourly_rate, paid, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    ("2026-01-10", "Client historique", 2, 22, 1, "2026-01-10T10:00:00", "2026-01-10T10:00:00"),
                )
            app_server.init_db()
            rows = app_server.list_interventions(2026, 1)
            assert len(rows) == 1 and rows[0]["amount_net"] == 44
            with app_server.db_connection() as db:
                assert db.execute("SELECT version FROM schema_migrations WHERE version = 2").fetchone()[0] == 2
                assert "status" in {row["name"] for row in db.execute("PRAGMA table_info(interventions)")}
                assert db.execute("SELECT payment_status FROM interventions WHERE id = 1").fetchone()[0] == "received"
                assert db.execute("SELECT COUNT(*) FROM intervention_notes").fetchone()[0] == 0
            backups = list((Path(os.environ["LOCALAPPDATA"]) / "EasyCESU" / "backups").glob("*avant-migration-v2*.zip"))
            assert backups
            """
        )

    def test_v2_categories_notes_and_pending_payments_are_explicit(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_client({"name": "Client V2", "activity": "jardinage", "usual_duration_hours": 2})
            category = app_server.create_service_category(
                {"name": "Taille", "activity": "jardinage", "default_hourly_rate": 25}
            )
            intervention = app_server.create_intervention(
                {
                    "date": "2026-07-19", "client": "Client V2", "duration_hours": 2, "hourly_rate": 22,
                    "category_id": category["id"], "status": "confirmee", "planned_start": "09:00", "planned_end": "11:00",
                }
            )
            assert intervention["category_id"] == category["id"]
            assert intervention["status"] == "confirmee"
            note = app_server.create_note(
                {"intervention_id": intervention["id"], "body": "Prévoir le pommier.", "category": "a_faire", "status": "a_faire", "carry_forward": True}
            )
            assert app_server.list_notes("Client V2", status="a_faire")[0]["id"] == note["id"]
            # Un paiement n'est créé que par l'action explicite correspondante, jamais par le texte de la note.
            assert app_server.list_pending_payments() == []
            payment = app_server.create_pending_payment(
                {"intervention_id": intervention["id"], "expected_amount": 44, "expected_date": "2026-07-25"}
            )
            assert payment["status"] == "a_recevoir"
            received = app_server.update_pending_payment(payment["id"], {"status": "recu", "received_amount": 44})
            assert received["status"] == "recu" and received["received_amount"] == 44
            """
        )

    def test_v3_document_templates_are_isolated_and_generate_a_pdf(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_client({"name": "Client V3"})
            app_server.create_intervention(
                {"date": "2026-07-12", "client": "Client V3", "duration_hours": 1.5, "hourly_rate": 22}
            )
            templates = app_server.list_document_templates()
            assert len(templates) == 1
            original = templates[0]
            assert original["is_default"] is True
            assert original["configuration"]["labels"]["title"] == "NOTE D’INTERVENTION"

            configuration = original["configuration"]
            configuration["labels"]["title"] = "RELEVÉ DES PRESTATIONS"
            configuration["table"]["header_background"] = "#D9ECF0"
            configuration["blocks"] = ["title", "identity", "table"]
            updated = app_server.update_document_template(
                original["id"],
                {"name": "Modèle personnalisé", "configuration": configuration, "is_default": True},
            )
            assert updated["configuration"]["blocks"][0] == "title"
            assert updated["configuration"]["table"]["header_background"] == "#D9ECF0"

            duplicate = app_server.duplicate_document_template(updated["id"])
            assert duplicate["id"] != updated["id"]
            assert duplicate["is_default"] is False
            app_server.delete_document_template(duplicate["id"])

            destination = Path(os.environ["EASY_CESU_TEST_WORKSPACE"])
            destination.mkdir(parents=True, exist_ok=True)
            test_pdf = app_server.generate_document_template_test_pdf(updated["configuration"], destination)
            assert test_pdf.read_bytes().startswith(b"%PDF")
            generated = app_server.generate_month_notes(2026, 7, output_dir=destination)
            note_path = Path(generated["notes"]["created"][0])
            assert note_path.exists() and note_path.read_bytes().startswith(b"%PDF")
            assert generated["template"]["name"] == "Modèle personnalisé"

            exported = app_server.export_document_template(updated["id"], destination)
            imported = app_server.import_document_template(exported)
            assert imported["name"] != updated["name"]
            assert imported["configuration"]["labels"]["title"] == "RELEVÉ DES PRESTATIONS"
            with app_server.db_connection() as db:
                assert db.execute("SELECT version FROM schema_migrations WHERE version = 3").fetchone()[0] == 3
                assert db.execute("SELECT COUNT(*) FROM interventions").fetchone()[0] == 1
                assert db.execute("SELECT COUNT(*) FROM clients").fetchone()[0] == 1
            """
        )

    def test_v3_local_server_starts_and_stops_without_a_browser(self) -> None:
        self.run_scenario(
            """
            import time
            import urllib.request

            runtime = app_server.LocalAppServer(preferred_port=0)
            url = runtime.start(background=True)
            port = runtime.port
            assert port > 0
            assert f":{port}/" in url
            with urllib.request.urlopen(url.replace("/?v=20260725-v300", "/api/app-info"), timeout=5) as response:
                info = __import__("json").loads(response.read().decode("utf-8"))
            assert info["app_version"] == "3.0.0"
            runtime.stop()
            time.sleep(0.2)
            assert app_server.port_is_listening(port) is False
            """
        )

    def test_macos_uses_application_support_and_native_dialogs(self) -> None:
        self.run_scenario(
            """
            import subprocess
            from pathlib import Path
            from unittest.mock import patch

            fake_home = Path(os.environ["EASY_CESU_TEST_WORKSPACE"]) / "mac-home"
            fake_home.mkdir(parents=True, exist_ok=True)
            with (
                patch.object(app_server.sys, "platform", "darwin"),
                patch.object(app_server.Path, "home", return_value=fake_home),
                patch.dict(os.environ, {"EASY_CESU_DATA_ROOT": ""}, clear=False),
            ):
                assert app_server.user_data_root() == fake_home / "Library" / "Application Support" / "EasyCESU"
                selected = subprocess.CompletedProcess([], 0, "/Users/test/Documents\\n", "")
                with patch.object(app_server.subprocess, "run", return_value=selected) as runner:
                    folder, cancelled = app_server.choose_folder("Choisir", fake_home)
                assert folder == Path("/Users/test/Documents")
                assert cancelled is False
                assert runner.call_args.args[0][0] == "/usr/bin/osascript"

                cancelled_result = subprocess.CompletedProcess([], 0, "__EASY_CESU_CANCELLED__\\n", "")
                with patch.object(app_server.subprocess, "run", return_value=cancelled_result):
                    file_path, cancelled = app_server.choose_file("Choisir", fake_home, "")
                assert file_path is None
                assert cancelled is True
            """
        )

    def test_monthly_reminder_keeps_the_reference_day_and_history(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_client({"name": "Client Rappel"})
            reminder = app_server.create_reminder(
                {
                    "client_name": "Client Rappel",
                    "title": "Contrat à vérifier",
                    "reference_date": "2026-01-31",
                    "recurrence_type": "monthly",
                    "recurrence_interval": 1,
                    "anticipation_value": 7,
                    "anticipation_unit": "days",
                }
            )
            occurrences = app_server.list_reminder_occurrences("Client Rappel", include_processed=True)
            due_dates = {item["due_date"] for item in occurrences}
            assert "2026-02-28" in due_dates
            assert "2026-03-31" in due_dates
            january = next(item for item in occurrences if item["due_date"] == "2026-01-31")
            app_server.set_reminder_occurrence_status(reminder["id"], january["id"], "completed")
            renamed = app_server.update_client("Client Rappel", {"name": "Client Rappel Renommé"})
            assert renamed["name"] == "Client Rappel Renommé"
            history = app_server.list_reminder_occurrences("Client Rappel Renommé", include_processed=True)
            assert any(item["status"] == "completed" for item in history)
            """
        )

    def test_yearly_reminder_handles_february_29_and_backup_zip(self) -> None:
        self.run_scenario(
            """
            app_server.init_db()
            app_server.create_client({"name": "Client Leap"})
            profile = app_server.active_profile()
            profile["suivi_paye_dir"] = r"\\serveur\\documents\\suivi"
            profile["fichier_clients"] = r"\\serveur\\documents\\clients.xlsx"
            app_server.save_config()
            reminder = app_server.create_reminder(
                {
                    "client_name": "Client Leap",
                    "title": "Attestation annuelle",
                    "reference_date": "2024-02-29",
                    "recurrence_type": "yearly",
                    "recurrence_interval": 1,
                    "anticipation_value": 1,
                    "anticipation_unit": "months",
                }
            )
            assert reminder["title"] == "Attestation annuelle"
            occurrences = app_server.list_reminder_occurrences("Client Leap", include_processed=True)
            assert any(item["due_date"] == "2025-02-28" for item in occurrences)
            assert any(item["due_date"] == "2026-02-28" for item in occurrences)
            backup = app_server.backup_profile_to(Path(os.environ["EASY_CESU_TEST_WORKSPACE"]))
            archive = Path(backup["backup"])
            assert archive.suffix == ".zip" and archive.exists()
            details = app_server.verify_backup(archive)
            assert details["profile"]["profile"]["id"] == app_server.active_profile()["id"]
            restored = app_server.restore_profile_from_backup(archive)
            assert restored["restored_profile"]["id"] != ""
            assert any(client["name"] == "Client Leap" for client in app_server.clients_list())
            assert Path(restored["backup_before_restore"]).exists()
            assert app_server.active_profile()["suivi_paye_dir"] == ""
            assert app_server.active_profile()["fichier_clients"] == ""
            import zipfile
            kit = Path(os.environ["EASY_CESU_TEST_WORKSPACE"]) / "Transfert_EasyCESU.zip"
            with zipfile.ZipFile(kit, "w", zipfile.ZIP_DEFLATED) as kit_file:
                kit_file.write(archive, "Transfert/Sauvegarde_EasyCESU_Exemple.zip")
            restored_from_kit = app_server.restore_profile_from_backup(kit)
            assert restored_from_kit["from_transfer_kit"] is True
            assert any(client["name"] == "Client Leap" for client in app_server.clients_list())
            malicious = Path(os.environ["EASY_CESU_TEST_WORKSPACE"]) / "archive-malveillante.zip"
            with zipfile.ZipFile(malicious, "w") as archive_file:
                archive_file.writestr("../hors-dossier.txt", "interdit")
            try:
                app_server.verify_backup(malicious)
            except ValueError:
                pass
            else:
                raise AssertionError("Une archive ZIP Slip devait être refusée")
            """
        )


if __name__ == "__main__":
    unittest.main()
