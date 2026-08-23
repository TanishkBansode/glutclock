#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
.venv/bin/python -m oracle_pc.pipeline run >> logs/cron.log 2>&1
