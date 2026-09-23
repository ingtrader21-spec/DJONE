# Production Candidate Certificate

A DJONE release may be labeled **PRODUCTION_CANDIDATE** when:
- exact source SHA is recorded;
- CI API tests and compose validation pass;
- API, PostgreSQL, Redis, Mixxx Bridge and webhook worker are healthy;
- safety is fail-closed;
- command/idempotency authority is durable;
- integration registry and webhook outbox/dead-letter authority are present;
- rollback source SHA and database backup are recorded.

**PRODUCTION_ENABLED** is a separate state and additionally requires native Mixxx ControlObject command/readback certification, idempotency effect proof, manual override and emergency-stop evidence.

Never set execution_enabled=true merely to obtain a release certificate.
