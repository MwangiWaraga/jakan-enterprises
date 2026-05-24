#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
python -m jakan.cli scrape-oraimo --load
