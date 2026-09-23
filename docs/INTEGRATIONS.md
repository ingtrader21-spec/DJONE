# DJONE Integration Architecture

Every DJONE domain is independently integrable. Domains own their core functionality, API endpoints, webhook events, workflow state machine and tests. No domain may bypass Commands/Safety for live effects.

## Integration modules

### 1. Core / System
Purpose: service discovery and operational truth.
Endpoints: GET /health, /ready, /v1/capabilities.
Webhooks: system.ready, system.degraded, system.recovered.
Workflow: BOOTING → READY → DEGRADED → READY/STOPPED.

### 2. Music Library
Purpose: storage, ingestion, hashes, metadata, analysis, provenance.
Endpoints: GET/POST /v1/library/tracks; GET /v1/library/tracks/{id}; POST /v1/library/imports.
Webhooks: library.track.registered, library.track.duplicate, library.track.analyzed, library.import.failed.
Workflow: RECEIVED → VALIDATED → HASHED → REGISTERED → ANALYZED → AVAILABLE.

### 3. Decks / Mixxx
Purpose: observed four-deck state and deck preparation.
Endpoints: GET /v1/decks, GET /v1/decks/{deck}; effectful actions flow through Commands.
Webhooks: deck.state.changed, deck.track.loaded, deck.play.started, deck.play.stopped, deck.readback.failed.
Workflow: DISCONNECTED → CONNECTED → EMPTY/LOADED → READY → PLAYING → STOPPED.

### 4. Commands
Purpose: sole effectful command authority.
Endpoints: POST /v1/commands; GET /v1/commands/{idempotency_key}.
Webhooks: command.validated, command.dispatched, command.completed, command.failed.
Workflow: RECEIVED → VALIDATED → POLICY_APPROVED → DISPATCHED → TRANSPORT_ACK → READBACK_VERIFIED → COMPLETED.

### 5. Safety
Purpose: fail-closed execution authority and operator override.
Endpoints: GET /v1/safety/status; POST /v1/safety/emergency-stop; POST /v1/safety/resume.
Webhooks: safety.stopped, safety.rearmed, safety.certified, safety.gate.changed.
Workflow: CLOSED → CERTIFIED → ARMED → STOPPED → REARM_PENDING → CLOSED/ARMED.

### 6. Sessions
Purpose: DJ set/session authority, play history and audit.
Endpoints: GET/POST /v1/sessions; GET /v1/sessions/{id}; GET /v1/sessions/{id}/events.
Webhooks: session.started, session.track.played, session.ended.
Workflow: CREATED → ACTIVE → PAUSED → ACTIVE → ENDED.

### 7. AI Agent
Purpose: planning and policy-constrained orchestration.
Endpoints: POST /v1/agent/plan; POST /v1/agent/execute.
Webhooks: agent.plan.created, agent.plan.approved, agent.plan.rejected, agent.execution.completed.
Workflow: PROMPT → CONTEXT → PLAN → POLICY → APPROVAL? → COMMANDS → RESULTS.

### 8. Remix
Purpose: asynchronous stems/rearrangement/generation/mastering.
Endpoints: GET /v1/remix/capabilities; GET/POST /v1/remix/jobs; GET /v1/remix/jobs/{id}.
Webhooks: remix.queued, remix.started, remix.completed, remix.failed.
Workflow: QUEUED → VALIDATED → PROCESSING → VALIDATING_OUTPUT → COMPLETED/FAILED.

## Webhook contract
Outbound webhook envelope:
- event_id UUID
- event_type
- occurred_at
- source = djone
- subject_type / subject_id
- correlation_id
- payload
- schema_version
- signature

Delivery is durable: event → outbox → signed delivery → ACK; retries use exponential backoff; terminal failures go to dead letter. Consumers must deduplicate by event_id.

## Middleware V3 integration
V3 gets a separate connector per domain rather than one unrestricted DJONE connector:
- djone-core
- djone-library
- djone-decks
- djone-commands
- djone-safety
- djone-sessions
- djone-agent
- djone-remix

V3 routes under /platform/v1/djone/* and subscribes to DJONE webhooks. Each connector has its own scopes, health, dependencies, SLOs and kill switch. V3 never talks directly to Mixxx.

## UI workflow
Dashboard navigation mirrors the domains: Overview | Decks | Library | Sessions | AI Agent | Remix | Integrations | Safety/Operations. Each page exposes its own status, workflow progress, errors, audit events and integration health.
