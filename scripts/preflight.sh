#!/usr/bin/env bash
set -euo pipefail
echo "== DJONE preflight =="
uname -a
command -v git
docker --version
docker compose version
echo "-- GPU --"
if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi; else echo "No nvidia-smi detected; CPU/non-NVIDIA profile required."; fi
echo "-- Audio --"
(command -v pactl >/dev/null && pactl info | head -n 12) || true
(command -v wpctl >/dev/null && wpctl status | head -n 40) || true
echo "Preflight complete."
