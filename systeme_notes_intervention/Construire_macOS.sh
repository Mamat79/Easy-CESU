#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

VERSION="$(tr -d '[:space:]' < VERSION)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BUILD_VENV="$ROOT/.build_venv_macos"
ARCH_LABEL="${EASY_CESU_MAC_ARCH_LABEL:-$(uname -m)}"
ICON="$ROOT/application/assets/easy-cesu.icns"
APP="$ROOT/dist/Easy CESU.app"
OUTPUT_DIR="$ROOT/sorties"
DMG="$OUTPUT_DIR/EasyCESU-macOS-${ARCH_LABEL}-${VERSION}.dmg"
NOTICE_SOURCE="$ROOT/output/pdf/Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "La construction macOS doit être exécutée sur un Mac." >&2
  exit 1
fi

if [[ ! -x "$BUILD_VENV/bin/python" ]]; then
  "$PYTHON_BIN" -m venv "$BUILD_VENV"
fi

PYTHON="$BUILD_VENV/bin/python"
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements-macos.txt
"$PYTHON" generer_icone.py
"$PYTHON" generer_notice_pdf.py
"$PYTHON" -m unittest tests.test_app_server_isolated tests.test_v3_native_window -v

rm -rf "$ROOT/build" "$ROOT/dist"
mkdir -p "$OUTPUT_DIR"

"$PYTHON" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "Easy CESU" \
  --icon "$ICON" \
  --osx-bundle-identifier "fr.easycesu.desktop" \
  --add-data "$ROOT/application/static:application/static" \
  --collect-data reportlab \
  "$ROOT/application/desktop_app.py"

cp "$NOTICE_SOURCE" "$APP/Contents/Resources/Easy_CESU_V3_Notice_Installation_et_Utilisation.pdf"
codesign --force --deep --sign - "$APP"
codesign --verify --deep --strict "$APP"
plutil -lint "$APP/Contents/Info.plist"

SMOKE_DATA="$(mktemp -d)"
SMOKE_LOG="$(mktemp)"
cleanup_smoke() {
  if [[ -n "${APP_PID:-}" ]] && kill -0 "$APP_PID" 2>/dev/null; then
    kill "$APP_PID" 2>/dev/null || true
    wait "$APP_PID" 2>/dev/null || true
  fi
  rm -rf "$SMOKE_DATA" "$SMOKE_LOG"
}
trap cleanup_smoke EXIT
EASY_CESU_DATA_ROOT="$SMOKE_DATA" "$APP/Contents/MacOS/Easy CESU" >"$SMOKE_LOG" 2>&1 &
APP_PID=$!
PORT=""
for _ in {1..40}; do
  if ! kill -0 "$APP_PID" 2>/dev/null; then
    cat "$SMOKE_LOG" >&2
    echo "L'application macOS s'est arrêtée pendant le test de lancement." >&2
    exit 1
  fi
  # lsof renvoie 1 tant que le serveur n'écoute pas encore. Ce délai normal
  # ne doit pas interrompre la boucle lorsque pipefail est actif.
  PORT="$(lsof -Pan -p "$APP_PID" -iTCP -sTCP:LISTEN 2>/dev/null | awk '/127[.]0[.]0[.]1:/ {sub(/^.*:/, "", $9); print $9; exit}' || true)"
  [[ -n "$PORT" ]] && break
  sleep 0.5
done
if [[ -z "$PORT" ]]; then
  cat "$SMOKE_LOG" >&2
  echo "Le serveur local de l'application macOS ne s'est pas ouvert." >&2
  kill "$APP_PID" 2>/dev/null || true
  exit 1
fi
APP_INFO="$(curl --fail --silent --show-error "http://127.0.0.1:${PORT}/api/app-info")"
"$PYTHON" -c 'import json,sys; data=json.loads(sys.argv[1]); assert data["app_version"] == sys.argv[2]' "$APP_INFO" "$VERSION"
cleanup_smoke
trap - EXIT

DMG_ROOT="$(mktemp -d)"
trap 'rm -rf "$DMG_ROOT"' EXIT
cp -R "$APP" "$DMG_ROOT/"
ln -s /Applications "$DMG_ROOT/Applications"
rm -f "$DMG"
hdiutil create \
  -volname "Easy CESU ${VERSION}" \
  -srcfolder "$DMG_ROOT" \
  -ov \
  -format UDZO \
  "$DMG"
hdiutil verify "$DMG"
shasum -a 256 "$DMG" > "$DMG.sha256"

echo "Application : $APP"
echo "Installateur : $DMG"
