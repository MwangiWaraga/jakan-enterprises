#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
docker compose up -d --build
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m jakan.cli init-db
echo "Bootstrap done. Metabase: http://localhost:3000"
