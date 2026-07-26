from __future__ import annotations

import os
import sys
from pathlib import Path


def configure_preview_runtime() -> None:
    """Isole les données d'une copie explicitement nommée V3 Preview."""

    executable_name = Path(sys.executable).stem.casefold()
    if getattr(sys, "frozen", False) and "v3 preview" in executable_name:
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support"
        else:
            base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
        os.environ.setdefault("EASY_CESU_DATA_ROOT", str(Path(base) / "EasyCESU-V3-Preview"))
        os.environ.setdefault("EASY_CESU_DISABLE_LEGACY_IMPORT", "1")


configure_preview_runtime()

from app_server import APP_NAME, APP_VERSION, LocalAppServer, user_data_root  # noqa: E402


def native_webview_gui() -> str:
    if sys.platform == "darwin":
        return "cocoa"
    return "edgechromium"


def main() -> int:
    try:
        import webview
    except ImportError as exc:
        raise RuntimeError("Le composant de fenêtre native pywebview est absent.") from exc

    # La fenêtre native ne publie pas un port fixe : le système lui attribue un
    # port local libre, sans risque de conflit avec une autre application.
    runtime = LocalAppServer(preferred_port=0)
    url = runtime.start(background=True)
    storage_dir = user_data_root() / "webview"
    storage_dir.mkdir(parents=True, exist_ok=True)
    debug = not getattr(sys, "frozen", False) and os.environ.get("EASY_CESU_WEBVIEW_DEBUG") == "1"

    try:
        webview.create_window(
            f"{APP_NAME} V{APP_VERSION.split('.')[0]}",
            url,
            width=1440,
            height=900,
            min_size=(1024, 680),
            background_color="#edf3f4",
            confirm_close=False,
        )
        webview.start(
            gui=native_webview_gui(),
            debug=debug,
            private_mode=False,
            storage_path=str(storage_dir),
        )
    finally:
        runtime.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
