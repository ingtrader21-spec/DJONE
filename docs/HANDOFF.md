# DJONE — Operator Handoff & Production Path

## Current machine
Codestra Ubuntu desktop. DJONE staging UI/API runs locally on port 8092. Mixxx runs natively. PostgreSQL, Redis and the Docker Mixxx Bridge run in Docker. The authenticated native adapter runs as a user service on port 18091.

## One manual Mixxx action
Open **Mixxx → Preferences → Controllers**.
1. Select **VirMIDI 1-0 / Virtual Raw MIDI 1-0**.
2. Enable the controller.
3. Select mapping **DJONE Native Bridge**.
4. Apply/OK.

Do not enable Auto-DJ execution yet.

## Certification after binding
Run `scripts/certify-mixxx.sh`. Expected pre-execution result:
- API health: pass
- API ready: pass
- Docker bridge: pass
- native_reachable: true
- transport_ready: true only after genuine Mixxx feedback
- execution_enabled: false

Then run a reversible Deck-1 test with no live program material, verify independent readback, ledger evidence, idempotency, emergency/manual override, and only then enable staging execution.

## Release progression
STAGING_READY → MIXXX_CERTIFIED → PRODUCTION_CANDIDATE → PRODUCTION_ENABLED.

Production enabled requires all evidence in docs/PRODUCTION.md. Never promote solely by changing DJONE_ENV.
