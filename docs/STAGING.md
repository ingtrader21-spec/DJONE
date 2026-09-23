# Staging Runbook

Staging is a certification environment, not permission for live AI deck execution.

## Required configuration
Set `DJONE_ENV=staging`, `DJONE_MODE=assistant`, a strong `DJONE_API_TOKEN`, and a non-default PostgreSQL password.

## Gate
1. CI test and compose jobs green.
2. `docker compose up -d --build`.
3. GET /health = 200.
4. GET /ready reports ready=true.
5. POST an allowlisted command with Bearer auth and Idempotency-Key.
6. Repeat the same key and verify the same command id.
7. Unknown action returns 422; missing/wrong token returns 401.
8. Mixxx execution remains false until bridge readback, emergency override, and durable ledger are implemented and certified.

No public ingress should expose PostgreSQL or Redis.
