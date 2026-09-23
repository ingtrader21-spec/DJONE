#!/usr/bin/env bash
set -euo pipefail
cd "${1:-$HOME/Desktop/DJONE}"
echo "== DJONE Mixxx native certification =="
H=$(docker compose exec -T mixxx-bridge python - <<'PY'
import json,urllib.request
print(urllib.request.urlopen('http://127.0.0.1:8091/health').read().decode())
PY
)
echo "$H"
python3 - "$H" <<'PY'
import json,sys
j=json.loads(sys.argv[1])
assert j["native_reachable"] is True, "native ControlObject API unreachable"
assert j["transport_ready"] is True, "native readback unavailable"
assert j["execution_enabled"] is False, "execution must remain closed during read-only certification"
print("NATIVE_READBACK_CERTIFIED=PASS")
PY
echo "Mutation/idempotency/override certification requires controlled execution arm and is a separate explicit gate."
