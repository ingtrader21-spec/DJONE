# Production Release Gate

DJONE production means a hardened, reproducible deployment candidate. It does not mean enabling unverified live deck automation.

## Required evidence
- CI green on exact release SHA.
- Staging API /health and /ready green.
- PostgreSQL and Redis healthy and non-public.
- Mixxx native process and audio engine healthy.
- Native Mixxx adapter proves command -> independent readback.
- Durable command ledger stores request, execution result and observed state.
- Idempotency replay proves no duplicate effect.
- Emergency/manual override test passes.
- Remix workers pass bounded input/output and failure tests.
- Secrets are external to Git and rotated for production.
- Backup/restore and rollback tested.

## Release states
- STAGING_READY: API/UI/data plane healthy, execution gate closed.
- PRODUCTION_CANDIDATE: immutable release artifact plus all automated tests green.
- PRODUCTION_ENABLED: requires native Mixxx readback certification and explicit execution-gate enablement.

Current target: reach PRODUCTION_CANDIDATE without bypassing the Mixxx readback gate.
