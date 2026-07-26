from __future__ import annotations

import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "application"))

import desktop_app


class FakeRuntime:
    def __init__(self) -> None:
        self.stopped = False

    def start(self, background: bool = True) -> str:
        if not background:
            raise AssertionError("La fenêtre native doit lancer le serveur en arrière-plan.")
        return "http://127.0.0.1:9999/?v=test"

    def stop(self) -> None:
        self.stopped = True


class NativeWindowTests(unittest.TestCase):
    def test_native_engine_matches_the_operating_system(self) -> None:
        with patch.object(desktop_app.sys, "platform", "darwin"):
            self.assertEqual(desktop_app.native_webview_gui(), "cocoa")
        with patch.object(desktop_app.sys, "platform", "win32"):
            self.assertEqual(desktop_app.native_webview_gui(), "edgechromium")

    def test_preview_named_executable_uses_an_isolated_data_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="easy-cesu-preview-root-") as temporary:
            with (
                patch.object(desktop_app.sys, "frozen", True, create=True),
                patch.object(desktop_app.sys, "executable", str(Path(temporary) / "Easy CESU V3 Preview.exe")),
                patch.dict(desktop_app.os.environ, {"LOCALAPPDATA": temporary}, clear=False),
            ):
                desktop_app.os.environ.pop("EASY_CESU_DATA_ROOT", None)
                desktop_app.configure_preview_runtime()
                self.assertEqual(
                    Path(desktop_app.os.environ["EASY_CESU_DATA_ROOT"]),
                    Path(temporary) / "EasyCESU-V3-Preview",
                )
                self.assertEqual(desktop_app.os.environ["EASY_CESU_DISABLE_LEGACY_IMPORT"], "1")
                desktop_app.os.environ.pop("EASY_CESU_DATA_ROOT", None)
                desktop_app.os.environ.pop("EASY_CESU_DISABLE_LEGACY_IMPORT", None)

    def test_macos_preview_uses_application_support(self) -> None:
        with tempfile.TemporaryDirectory(prefix="easy-cesu-preview-macos-") as temporary:
            with (
                patch.object(desktop_app.sys, "frozen", True, create=True),
                patch.object(desktop_app.sys, "platform", "darwin"),
                patch.object(desktop_app.sys, "executable", "/Applications/Easy CESU V3 Preview.app"),
                patch.object(desktop_app.Path, "home", return_value=Path(temporary)),
            ):
                desktop_app.os.environ.pop("EASY_CESU_DATA_ROOT", None)
                desktop_app.os.environ.pop("EASY_CESU_DISABLE_LEGACY_IMPORT", None)
                desktop_app.configure_preview_runtime()
                self.assertEqual(
                    Path(desktop_app.os.environ["EASY_CESU_DATA_ROOT"]),
                    Path(temporary) / "Library" / "Application Support" / "EasyCESU-V3-Preview",
                )
                desktop_app.os.environ.pop("EASY_CESU_DATA_ROOT", None)
                desktop_app.os.environ.pop("EASY_CESU_DISABLE_LEGACY_IMPORT", None)

    def test_native_window_uses_edgechromium_and_stops_its_server(self) -> None:
        runtime = FakeRuntime()
        calls: dict[str, object] = {}

        def create_runtime(*args: object, **kwargs: object) -> FakeRuntime:
            calls["runtime"] = (args, kwargs)
            return runtime

        def create_window(*args: object, **kwargs: object) -> None:
            calls["create"] = (args, kwargs)

        def start(**kwargs: object) -> None:
            calls["start"] = kwargs

        fake_webview = types.SimpleNamespace(create_window=create_window, start=start)
        with tempfile.TemporaryDirectory(prefix="easy-cesu-native-") as temporary:
            with (
                patch.object(desktop_app, "LocalAppServer", side_effect=create_runtime),
                patch.object(desktop_app, "user_data_root", return_value=Path(temporary)),
                patch.dict(sys.modules, {"webview": fake_webview}),
            ):
                result = desktop_app.main()

        self.assertEqual(result, 0)
        self.assertTrue(runtime.stopped)
        self.assertEqual(calls["runtime"], ((), {"preferred_port": 0}))
        title, url = calls["create"][0][:2]
        self.assertEqual(title, "Easy CESU V3")
        self.assertEqual(url, "http://127.0.0.1:9999/?v=test")
        self.assertEqual(calls["start"]["gui"], "edgechromium")
        self.assertFalse(calls["start"]["private_mode"])

    def test_native_window_stops_server_when_webview_fails(self) -> None:
        runtime = FakeRuntime()
        fake_webview = types.SimpleNamespace(
            create_window=lambda *args, **kwargs: None,
            start=lambda **kwargs: (_ for _ in ()).throw(RuntimeError("WebView2 indisponible")),
        )
        with tempfile.TemporaryDirectory(prefix="easy-cesu-native-") as temporary:
            with (
                patch.object(desktop_app, "LocalAppServer", return_value=runtime),
                patch.object(desktop_app, "user_data_root", return_value=Path(temporary)),
                patch.dict(sys.modules, {"webview": fake_webview}),
            ):
                with self.assertRaisesRegex(RuntimeError, "WebView2 indisponible"):
                    desktop_app.main()
        self.assertTrue(runtime.stopped)


if __name__ == "__main__":
    unittest.main()
