#!/usr/bin/env bash
# Golden Core — one-shot local launcher
set -e

cd "$(dirname "$0")/backend"

if [ ! -d ".venv" ]; then
  echo "[setup] creating virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

if [ -z "$GROQ_API_KEY" ]; then
  echo "!! GROQ_API_KEY is not set."
  echo "   Create a free key at https://console.groq.com/keys"
  echo "   export GROQ_API_KEY=your-key-here   (then re-run this script)"
  exit 1
fi

echo "[start] Golden Core backend on http://localhost:8000"
echo "[start] Open http://localhost:8000 in Chrome."
uvicorn main:app --reload --port 8000
