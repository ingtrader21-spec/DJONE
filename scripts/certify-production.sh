#!/usr/bin/env bash
set -euo pipefail
BASE="${DJONE_URL:-http://127.0.0.1:8092}"
echo "== DJONE production certificate =="
READY=$(curl -fsS "$BASE/ready")
PROD=$(curl -fsS "$BASE/v1/production/status")
EVIDENCE=$(curl -fsS "$BASE/v1/certification/evidence")
python3 - "$READY" "$PROD" "$EVIDENCE" <<'PY'
import json,sys
ready,prod,evidence=map(json.loads,sys.argv[1:])
assert ready["ready"] is True
assert prod["production_candidate"] is True
s=evidence["safety"]
assert s["certified"] is True
assert s["manual_override"] is True
assert evidence["native_mutation"] and evidence["native_mutation"]["payload"].get("result")=="PASS"
print("PRODUCTION_CANDIDATE_CERTIFICATE=PASS")
print("PRODUCTION_ENABLED="+("YES" if prod["production_enabled"] else "NO"))
if not prod["production_enabled"]: print("ACTIVE_BLOCKERS="+",".join(prod["blockers"]))
PY
