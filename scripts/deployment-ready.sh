#!/usr/bin/env bash
set -euo pipefail
cd "${1:-$HOME/Desktop/DJONE}"
echo "== DJONE deployment readiness =="
docker compose config >/dev/null
curl -fsS http://127.0.0.1:${DJONE_HTTP_PORT:-8092}/health >/dev/null
curl -fsS http://127.0.0.1:${DJONE_HTTP_PORT:-8092}/ready >/dev/null
curl -fsS http://127.0.0.1:${DJONE_HTTP_PORT:-8092}/v1/integrations >/dev/null
curl -fsS http://127.0.0.1:${DJONE_HTTP_PORT:-8092}/v1/safety/status | grep -q '"fail_closed":true'
docker compose exec -T postgres pg_isready -U djone -d djone
docker compose ps
echo "DEPLOYMENT_READY_FOUNDATION=PASS"
echo "LIVE_MIXXX_EXECUTION_CERTIFIED=NO"
