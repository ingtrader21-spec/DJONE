# DJONE API & Workflow Design Freeze

## Principles
1. Mixxx observed state is authoritative for live deck state.
2. PostgreSQL is authoritative for commands, jobs, sessions and audit.
3. Redis is coordination/cache only.
4. AI never calls Mixxx directly; all effects pass policy + idempotency + safety.
5. Transport success is not execution success. A command is complete only after independent readback.
6. Manual controls and emergency stop outrank automation.
7. Production defaults fail closed.

## Bounded contexts
- **System:** health, readiness, capabilities.
- **Decks:** read-only observed state for four decks.
- **Commands:** one effectful command envelope and lifecycle.
- **Agent:** plan first; execution is separately authorized.
- **Remix:** asynchronous stems/cover/repaint/arrange jobs.
- **Library:** track ingest, metadata, analysis, generated assets.
- **Sessions:** set lifecycle and immutable event history.
- **Safety:** execution gate, emergency stop, re-arm.

## Command lifecycle
RECEIVED → VALIDATED → POLICY_APPROVED → DISPATCHED → TRANSPORT_ACK → READBACK_VERIFIED → COMPLETED.
Failure states: REJECTED, TRANSPORT_FAILED, READBACK_FAILED, CANCELLED, EMERGENCY_STOPPED.

Every command carries: command_id, idempotency_key, actor, mode, session_id, action, target, requested value, timestamps, policy decision, transport result, observed value, final status.

## Agent workflow
Prompt → context snapshot → non-effectful plan → policy evaluation → operator approval when required → commands → Mixxx API → readback → ledger → UI event.

Assistant: recommendations only.
Copilot: may prepare approved reversible actions.
Auto-DJ: may execute allowlisted policy-approved actions only while explicitly armed.

## Remix workflow
Source → validation/hash → analysis → optional stems → generation/rearrangement → mastering → artifact validation → library registration → optional deck preparation. Remix jobs never load/play a deck implicitly.

## Production API boundary
Only the DJONE API is exposed to the UI. PostgreSQL, Redis, Mixxx native API and workers remain private. Native Mixxx API binds localhost and accepts only service authentication.

## Versioning
Public contract is /v1. Breaking changes require /v2. OpenAPI is the source of truth and CI must validate operation IDs and route parity.
