from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import installateur_windows


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class InstallerV210Tests(unittest.TestCase):
    def test_versions_are_synchronized(self) -> None:
        version = (PROJECT_ROOT / "VERSION").read_text(encoding="utf-8").strip()
        self.assertEqual(version, "2.1.0")
        self.assertEqual(installateur_windows.APP_VERSION, version)
        self.assertEqual(installateur_windows.shortcut_label(), "Easy CESU V2.1.0")

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
        self.assertIn("par 30 min", html)
        self.assertIn("par 0,50 €", html)
        self.assertIn("function adjustSteppedNumber", javascript)
        self.assertIn("const step = 0.5", javascript)


if __name__ == "__main__":
    unittest.main()
