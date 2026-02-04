#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env}"
SERVICE_NAME="${SERVICE_NAME:-scoutscope-bot}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing .env at $ENV_FILE"
  echo "Create it from .env.example before deploying."
  exit 1
fi

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python not found: $PYTHON_BIN"
  exit 1
fi

"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# Optional: create data dir for persistent storage
mkdir -p "$APP_DIR/data"

start_app() {
  local python="$VENV_DIR/bin/python"

  if [[ ! -x "$python" ]]; then
    echo "Virtualenv python not found: $python"
    exit 1
  fi

  if command -v systemctl >/dev/null 2>&1; then
    if systemctl list-unit-files --type=service --no-pager 2>/dev/null | awk '{print $1}' | grep -qx "${SERVICE_NAME}.service"; then
      echo "Restarting systemd service: ${SERVICE_NAME}.service"
      if systemctl restart "${SERVICE_NAME}.service"; then
        return
      fi
      echo "systemctl restart failed; falling back to background start."
    fi
  fi

  if command -v pgrep >/dev/null 2>&1; then
    if pgrep -f "$APP_DIR/main.py" >/dev/null 2>&1; then
      echo "App already running."
      return
    fi
  fi

  mkdir -p "$APP_DIR/data"
  nohup "$python" "$APP_DIR/main.py" > "$APP_DIR/data/app.log" 2>&1 &
  echo $! > "$APP_DIR/data/app.pid"
  echo "App started in background (pid $!)."
}

start_app
echo "Deploy complete."
