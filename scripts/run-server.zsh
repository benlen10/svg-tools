#!/usr/bin/env zsh
set -euo pipefail

APP_DIR="/Users/blenington/Github/svg-tools"
cd "$APP_DIR"

export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PYTHONUNBUFFERED=1
export FLASK_DEBUG=0
export PORT="${PORT:-5011}"

mkdir -p "$APP_DIR/logs"

python_bin="${SVG_TOOLS_PYTHON:-}"
if [[ -z "$python_bin" ]]; then
  for candidate in \
    /opt/homebrew/opt/python@3.14/bin/python3.14 \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /usr/bin/python3; do
    if [[ -x "$candidate" ]]; then
      python_bin="$candidate"
      break
    fi
  done
fi

if [[ -z "$python_bin" ]]; then
  echo "No usable python3 found" >&2
  exit 70
fi

venv_ok() {
  [[ -x .venv/bin/python ]] || return 1
  .venv/bin/python - <<'PY'
import flask
import cv2
import numpy
from PIL import Image
import app
PY
}

if ! venv_ok; then
  echo "Rebuilding svg-tools virtualenv with $python_bin"
  rm -rf .venv
  "$python_bin" -m venv --clear .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install --requirement requirements.lock
fi

exec .venv/bin/python app.py
