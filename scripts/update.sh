#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$APP_DIR/venv}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env}"
REPO_URL="${REPO_URL:-https://github.com/Tw1zzzzz/twizz_bot-}"
SERVICE_NAME="${SERVICE_NAME:-scoutscope-bot}"
BRANCH="${BRANCH:-$(git -C "$APP_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || true)}"

normalize_repo_url() {
  local url="${1%/}"
  url="${url%.git}"
  url="${url#git@github.com:}"
  url="${url#ssh://git@github.com/}"
  url="${url#https://github.com/}"
  url="${url#http://github.com/}"
  echo "$url"
}

ensure_git_sync() {
  cd "$APP_DIR"

  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Not a git repository: $APP_DIR"
    echo "Clone from $REPO_URL first."
    exit 1
  fi

  local current_url
  current_url="$(git remote get-url origin 2>/dev/null || true)"
  if [[ -z "$current_url" ]]; then
    git remote add origin "$REPO_URL"
    current_url="$REPO_URL"
  fi

  local expected_norm current_norm
  expected_norm="$(normalize_repo_url "$REPO_URL")"
  current_norm="$(normalize_repo_url "$current_url")"

  if [[ "$current_norm" != "$expected_norm" ]]; then
    echo "Origin remote does not match expected repo."
    echo "Expected repo: $REPO_URL"
    echo "Found remote: $current_url"
    echo "Set REPO_URL if you want another repository."
    exit 1
  fi

  local target_branch="$BRANCH"
  if [[ -z "$target_branch" || "$target_branch" == "HEAD" ]]; then
    local origin_head
    origin_head="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)"
    target_branch="${origin_head#origin/}"
  fi

  if [[ -z "$target_branch" || "$target_branch" == "HEAD" ]]; then
    echo "Could not detect target branch. Set BRANCH=<name>."
    exit 1
  fi

  echo "Syncing code from origin/$target_branch"
  git fetch --prune origin
  git pull --ff-only origin "$target_branch"
}

prepare_runtime() {
  if [[ ! -f "$ENV_FILE" ]]; then
    echo "Missing .env at $ENV_FILE"
    echo "Create it from .env.example before updating."
    exit 1
  fi

  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python not found: $PYTHON_BIN"
    exit 1
  fi

  "$PYTHON_BIN" -m venv "$VENV_DIR"
  "$VENV_DIR/bin/pip" install --upgrade pip
  "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
}

restart_app() {
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

  if [[ -f "$APP_DIR/data/app.pid" ]]; then
    local old_pid
    old_pid="$(cat "$APP_DIR/data/app.pid" 2>/dev/null || true)"
    if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
      echo "Stopping previous app process from pid file: $old_pid"
      kill "$old_pid" || true
      sleep 1
    fi
    rm -f "$APP_DIR/data/app.pid"
  fi

  if command -v pgrep >/dev/null 2>&1; then
    local stale_pids
    stale_pids="$(pgrep -f "$APP_DIR/main.py" || true)"
    if [[ -n "$stale_pids" ]]; then
      echo "Stopping stale app process(es): $stale_pids"
      # shellcheck disable=SC2086
      kill $stale_pids || true
      sleep 1
    fi
  fi

  mkdir -p "$APP_DIR/data"
  nohup "$python" "$APP_DIR/main.py" > "$APP_DIR/data/app.log" 2>&1 &
  echo $! > "$APP_DIR/data/app.pid"
  echo "App started in background (pid $!)."
}

ensure_git_sync
prepare_runtime
restart_app
echo "Update complete."
