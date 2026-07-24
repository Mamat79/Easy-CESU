from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
runtime_root = Path(os.environ["EASY_CESU_PREVIEW_DATA"])
runtime_root.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(runtime_root)

# Reproduit les chemins de l'application empaquetée sans toucher aux données réelles.
sys.frozen = True
sys._MEIPASS = str(PROJECT_ROOT)
sys.executable = str(runtime_root / "Easy CESU.exe")
sys.path.insert(0, str(PROJECT_ROOT / "application"))
sys.path.insert(0, str(PROJECT_ROOT))

import app_server


raise SystemExit(app_server.main(open_browser=False))
