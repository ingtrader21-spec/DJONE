#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$HOME/Desktop/DJONE}"
cd "$ROOT"
PORT="${DJONE_HTTP_PORT:-8092}"
echo "== DJONE certification =="
echo "-- containers --"; docker compose ps
echo "-- API health --"; curl -fsS "http://127.0.0.1:$PORT/health"; echo
echo "-- API readiness --"; curl -fsS "http://127.0.0.1:$PORT/ready"; echo
echo "-- Mixxx process --"; pgrep -a mixxx || { echo "FAIL: Mixxx not running"; exit 2; }
echo "-- native adapter --"; systemctl --user is-active djone-mixxx-adapter.service
echo "-- MIDI --"; aconnect -l
echo "-- bridge health --"
docker compose exec -T mixxx-bridge python - <<'PY'
import json,urllib.request,sys
j=json.load(urllib.request.urlopen("http://127.0.0.1:8091/health"))
print(json.dumps(j,indent=2))
if not j.get("native_reachable"): sys.exit(3)
if j.get("execution_enabled"): 
 print("FAIL: execution must remain closed before certification"); sys.exit(4)
if not j.get("transport_ready"):
 print("PENDING: native path works but Mixxx feedback is not certified"); sys.exit(5)
print("PASS: transport reports ready; proceed to reversible readback test.")
PY
