#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
REPO_URL="${REPO_URL:-https://github.com/Tw1zzzzz/twizz_bot-}"
SERVICE_NAME="${SERVICE_NAME:-scoutscope-bot}"

cd "$APP_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Not a git repository: $APP_DIR"
  exit 1
fi

CURRENT_URL="$(git remote get-url origin 2>/dev/null || true)"
if [[ -z "$CURRENT_URL" ]]; then
  git remote add origin "$REPO_URL"
  CURRENT_URL="$REPO_URL"
fi

if [[ "$CURRENT_URL" != "$REPO_URL" ]]; then
  echo "Origin remote does not match expected repo."
  echo "Expected: $REPO_URL"
  echo "Found: $CURRENT_URL"
  echo "Set REPO_URL to override or fix the origin remote."
  exit 1
fi

BRANCH="${BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
if [[ "$BRANCH" == "HEAD" ]]; then
  echo "Detached HEAD. Set BRANCH to the target branch."
  exit 1
fi

git fetch origin
git pull --ff-only origin "$BRANCH"

if [[ -d "$VENV_DIR" ]]; then
  "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
fi

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
echo "Update complete."
