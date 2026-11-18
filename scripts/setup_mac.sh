#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo 'Python 3 missing'; exit 1; }
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; echo 'Created .env: SET LLM_MODEL to the exact LM Studio model ID'; fi
printf '\nSetup done. Start LM Studio server, Docker Qdrant, then run README instructions.\n'
