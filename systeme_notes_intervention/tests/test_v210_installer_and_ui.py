from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import installateur_windows


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class InstallerV3Tests(unittest.TestCase):
    def test_versions_are_synchronized(self) -> None:
        version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "3.1.4")
        self.assertEqual(installateur_windows.APP_VERSION, version)
        self.assertEqual(installateur_windows.shortcut_label(), "Easy CESU V3.1.4")

    def test_packaging_includes_the_note_generator(self) -> None:
        build_script = (PROJECT_ROOT / "Construire_executable.ps1").read_text(encoding="utf-8")
        self.assertIn("--paths $Root", build_script)
        self.assertIn("--hidden-import generer_notes_et_donnees", build_script)
        macos_build_script = (PROJECT_ROOT / "Construire_macOS.sh").read_text(encoding="utf-8")
        self.assertIn('--paths "$ROOT"', macos_build_script)
        self.assertIn("--hidden-import generer_notes_et_donnees", macos_build_script)

    def test_every_installer_choice_has_an_icon_and_preview(self) -> None:
        for icon_key in installateur_windows.SHORTCUT_ICON_LABELS:
            self.assertTrue(
                installateur_windows.shortcut_icon_source_path(icon_key).is_file(),
                icon_key,
            )
            self.assertTrue(
                installateur_windows.shortcut_icon_preview_path(icon_key).is_file(),
                icon_key,
            )

    def test_elevated_arguments_keep_the_selected_icon(self) -> None:
        _, arguments = installateur_windows.elevated_install_args(
            Path(r"C:\Program Files\Easy CESU"),
            True,
            True,
            False,
            False,
            "menage",
        )
        self.assertIn("--shortcut-icon", arguments)
        self.assertEqual(arguments[arguments.index("--shortcut-icon") + 1], "menage")

    def test_webview2_is_installed_only_when_missing(self) -> None:
        with patch.object(installateur_windows, "webview2_runtime_version", return_value="150.0.0.0"):
            with patch.object(installateur_windows.subprocess, "run") as run:
                self.assertEqual(installateur_windows.ensure_webview2_runtime(), "150.0.0.0")
                run.assert_not_called()

        with tempfile.TemporaryDirectory(prefix="easy-cesu-webview2-") as temporary:
            bootstrapper = Path(temporary) / installateur_windows.WEBVIEW2_BOOTSTRAPPER_NAME
            bootstrapper.write_bytes(b"programme de test")
            completed = type("Completed", (), {"returncode": 0})()
            with (
                patch.object(installateur_windows, "webview2_bootstrapper_path", return_value=bootstrapper),
                patch.object(
                    installateur_windows,
                    "webview2_runtime_version",
                    side_effect=["", "150.0.0.0"],
                ),
                patch.object(installateur_windows.subprocess, "run", return_value=completed) as run,
            ):
                self.assertEqual(installateur_windows.ensure_webview2_runtime(), "150.0.0.0")
                run.assert_called_once()
                self.assertEqual(run.call_args.args[0][1:], ["/silent", "/install"])

    def test_legacy_local_installation_is_detected_for_replacement(self) -> None:
        with tempfile.TemporaryDirectory(prefix="easy-cesu-detection-") as temporary:
            root = Path(temporary)
            legacy_install = root / "Easy CESU"
            legacy_install.mkdir()
            (legacy_install / "Easy CESU.exe").write_bytes(b"ancienne version")
            environment = {
                "LOCALAPPDATA": str(root),
                "APPDATA": str(root / "Roaming"),
                "USERPROFILE": str(root / "User"),
            }
            with patch.dict(os.environ, environment):
                installations = installateur_windows.detect_existing_installations(Path(r"C:\Program Files\Easy CESU"))
            self.assertIn(legacy_install.resolve(), installations)

    def test_existing_profile_icon_is_detected_and_updated_without_other_changes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="easy-cesu-installer-") as temporary:
            local_app_data = Path(temporary)
            config_path = local_app_data / "EasyCESU" / "config" / "config.json"
            config_path.parent.mkdir(parents=True)
            original = {
                "active_profile_id": "compte-test",
                "profiles": [
                    {
                        "id": "compte-test",
                        "label": "Compte test",
                        "primary_activity": "jardinage",
                        "shortcut_icon": "jardinage",
                        "data_file": "base-a-conserver.sqlite",
                    }
                ],
            }
            config_path.write_text(json.dumps(original), encoding="utf-8")
            with patch.dict(os.environ, {"LOCALAPPDATA": str(local_app_data)}):
                self.assertEqual(installateur_windows.configured_shortcut_icon(), "jardinage")
                installateur_windows.remember_shortcut_icon("informatique")

            updated = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["profiles"][0]["shortcut_icon"], "informatique")
            self.assertEqual(updated["profiles"][0]["data_file"], "base-a-conserver.sqlite")

    def test_payload_replacement_preserves_legacy_data_and_configuration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="easy-cesu-update-") as temporary:
            root = Path(temporary)
            source = root / "payload"
            destination = root / "Easy CESU"
            (source / "_internal").mkdir(parents=True)
            (source / "_internal" / "runtime.bin").write_bytes(b"nouveau moteur")
            (source / installateur_windows.EXE_NAME).write_bytes(b"nouvel executable")
            (source / installateur_windows.NOTICE_NAME).write_bytes(b"nouvelle notice")

            (destination / "_internal").mkdir(parents=True)
            (destination / "_internal" / "runtime.bin").write_bytes(b"ancien moteur")
            (destination / "application" / "data").mkdir(parents=True)
            (destination / "application" / "data" / "clients.sqlite").write_bytes(b"donnees")
            (destination / "config.json").write_text('{"profil":"Clotilde"}', encoding="utf-8")
            old_notice = destination / "Easy_CESU_V2_Notice_Installation_et_Utilisation.pdf"
            old_notice.write_bytes(b"ancienne notice")

            installateur_windows.replace_application_payload(source, destination)
            installateur_windows.remove_obsolete_notices(destination)

            self.assertEqual(
                (destination / "_internal" / "runtime.bin").read_bytes(),
                b"nouveau moteur",
            )
            self.assertEqual(
                (destination / installateur_windows.EXE_NAME).read_bytes(),
                b"nouvel executable",
            )
            self.assertEqual(
                (destination / "application" / "data" / "clients.sqlite").read_bytes(),
                b"donnees",
            )
            self.assertEqual(
                (destination / "config.json").read_text(encoding="utf-8"),
                '{"profil":"Clotilde"}',
            )
            self.assertFalse(old_notice.exists())
            retired = list(destination.glob("_internal.precedente-*"))
            self.assertEqual(len(retired), 1)
            self.assertEqual(
                (retired[0] / "runtime.bin").read_bytes(),
                b"ancien moteur",
            )


class NumericStepperContractTests(unittest.TestCase):
    def test_large_steppers_cover_duration_and_money_fields(self) -> None:
        html = (PROJECT_ROOT / "application" / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (PROJECT_ROOT / "application" / "static" / "app.js").read_text(encoding="utf-8")
        for field in (
            "durationInput",
            "rateInput",
            "plannedAmountInput",
            "receivedAmountInput",
            "defaultRateInput",
            "clientRateInput",
            "paymentAmountInput",
        ):
            self.assertIn(f'data-step-target="{field}"', html)
        self.assertNotIn("stepper-hint", html)
        self.assertNotIn("par 30 min", html)
        self.assertNotIn("par 0,50 €", html)
        self.assertIn('id="durationInput" type="text"', html)
        self.assertIn("function parseDurationInput", javascript)
        self.assertIn("function formatDurationInput", javascript)
        self.assertIn('els.durationInput.value = "1:00"', javascript)
        self.assertIn("function adjustSteppedNumber", javascript)
        self.assertIn("const step = 0.5", javascript)


class DisplayScalingContractTests(unittest.TestCase):
    def test_display_modes_are_local_and_immediately_accessible(self) -> None:
        html = (PROJECT_ROOT / "application" / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (PROJECT_ROOT / "application" / "static" / "app.js").read_text(encoding="utf-8")
        stylesheet = (PROJECT_ROOT / "application" / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn('id="displayModeSelect"', html)
        for mode in ("auto", "compact", "normal", "large"):
            self.assertIn(f'value="{mode}"', html)
        self.assertIn('const storageKey = "easyCesuDisplayMode"', html)
        self.assertIn("localStorage.getItem(storageKey)", html)
        self.assertIn('const DISPLAY_STORAGE_KEY = "easyCesuDisplayMode"', javascript)
        self.assertIn("function automaticDisplayScale", javascript)
        self.assertIn("1 / dpr", javascript)
        self.assertIn("document.documentElement.style.zoom", javascript)
        self.assertIn("localStorage.setItem(DISPLAY_STORAGE_KEY, mode)", javascript)
        self.assertIn(".display-control", stylesheet)


class InterventionAddressContractTests(unittest.TestCase):
    def test_location_is_hidden_and_follows_the_selected_client(self) -> None:
        html = (PROJECT_ROOT / "application" / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (PROJECT_ROOT / "application" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertIn('id="locationInput" type="hidden"', html)
        self.assertNotIn('<label for="locationInput">', html)
        self.assertNotIn(">Lieu<", html)
        self.assertIn('els.locationInput.value = client.address || ""', javascript)
        self.assertIn('els.clientInput.addEventListener("input", applySelectedClientDefaults)', javascript)


class EmailNotesContractTests(unittest.TestCase):
    def test_client_defaults_smtp_templates_and_review_dialog_are_visible(self) -> None:
        html = (PROJECT_ROOT / "application" / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (PROJECT_ROOT / "application" / "static" / "app.js").read_text(encoding="utf-8")
        server = (PROJECT_ROOT / "application" / "app_server.py").read_text(encoding="utf-8")

        for element_id in (
            "emailNotesBtn",
            "clientEmailNotesInput",
            "clientEmailReviewInput",
            "smtpHostInput",
            "smtpPasswordInput",
            "emailSubjectTemplateInput",
            "emailBodyTemplateInput",
            "emailNotesDialog",
            "emailReviewDialog",
            "emailMarkTransmittedInput",
        ):
            self.assertIn(f'id="{element_id}"', html)
        for placeholder in ("{client}", "{mois}", "{annee}", "{heures}", "{montant}", "{nom}"):
            self.assertIn(placeholder, html)
        self.assertIn("function openEmailNotesDialog", javascript)
        self.assertIn("function showNextEmailForReview", javascript)
        self.assertIn('"/api/send-month-emails"', javascript)
        self.assertIn("email_review_before_send", server)
        self.assertIn("message_overrides", server)
        self.assertIn("mark_transmitted: state.emailMarkTransmitted", javascript)
        self.assertIn('id="emailMarkTransmittedInput" type="checkbox" />', html)


class AdministrativeFollowupContractTests(unittest.TestCase):
    def test_three_direct_states_and_followup_controls_are_visible(self) -> None:
        html = (PROJECT_ROOT / "application" / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (PROJECT_ROOT / "application" / "static" / "app.js").read_text(encoding="utf-8")
        server = (PROJECT_ROOT / "application" / "app_server.py").read_text(encoding="utf-8")

        self.assertIn('data-view="followup">Notes et paiements', html)
        for element_id in (
            "declaredInput",
            "followupTypeFilter",
            "followupSearchInput",
            "followupShowIgnoredInput",
            "interventionFollowupsBody",
        ):
            self.assertIn(f'id="{element_id}"', html)
        transmitted = html.index('class="status-col">Transmis</th>')
        declared = html.index('class="status-col" title="Déclaré auprès du CESU">Déclaré</th>')
        paid = html.index('class="status-col">Payé</th>')
        self.assertLess(transmitted, declared)
        self.assertLess(declared, paid)
        self.assertIn('data-administrative-status="${reminderType}"', javascript)
        self.assertIn("administrativeStatusRequests.has(requestKey)", javascript)
        self.assertIn("state.administrativeStatusRequests.add(requestKey)", javascript)
        self.assertIn("state.administrativeStatusRequests.delete(requestKey)", javascript)
        self.assertIn("/administrative-status", javascript)
        self.assertIn("intervention_followup_ignores", server)
        self.assertIn("UNIQUE(intervention_id, reminder_type)", server)
        self.assertIn("ON DELETE CASCADE", server)


class CommunitySupportContractTests(unittest.TestCase):
    def test_funding_and_interface_are_limited_to_easy_cesu(self) -> None:
        repository_root = PROJECT_ROOT.parent
        funding = (repository_root / ".github" / "FUNDING.yml").read_text(encoding="utf-8")
        readme = (repository_root / "README.md").read_text(encoding="utf-8")
        html = (PROJECT_ROOT / "application" / "static" / "index.html").read_text(encoding="utf-8")
        javascript = (PROJECT_ROOT / "application" / "static" / "app.js").read_text(encoding="utf-8")

        self.assertEqual(
            funding,
            'custom:\n  - "https://www.paypal.com/paypalme/MamatLeroy"\n',
        )
        self.assertNotIn("sponsors", funding.lower())
        self.assertNotIn("sponsors", readme.lower())
        self.assertNotIn("sponsors", html.lower())
        for element_id in (
            "githubSourceBtn",
            "githubStarBtn",
            "githubIssueBtn",
            "paypalSupportBtn",
            "supportDialog",
            "supportDialogPayPalBtn",
            "supportReminderEnabledInput",
            "supportReminder",
        ):
            self.assertIn(f'id="{element_id}"', html)
        self.assertIn('openExternal("github_repository")', javascript)
        self.assertIn('openExternal("github_issues")', javascript)
        self.assertIn("showSupportDialog", javascript)
        self.assertIn('openExternal("paypal_me")', javascript)
        self.assertNotIn("paypal.com/qrcodes", javascript)
        self.assertIn("/assets/paypal-support-qr.png", html)
        qr_asset = PROJECT_ROOT / "application" / "static" / "assets" / "paypal-support-qr.png"
        self.assertTrue(qr_asset.is_file())


if __name__ == "__main__":
    unittest.main()
