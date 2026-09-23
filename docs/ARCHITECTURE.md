# Architecture

DJONE separates real-time audio from orchestration.

- **Mixxx (native):** playback, decks, mixer, effects, controllers, recording.
- **Control API:** authenticated command boundary and state API.
- **Mixxx Bridge:** allowlisted commands and readback; no arbitrary shell execution.
- **DJ Agent:** planning/recommendations and policy-constrained automation.
- **Remix pipeline:** source -> stems -> analysis -> generation/arrangement -> mastering -> library.
- **Data:** PostgreSQL for durable state/audit; Redis for ephemeral coordination.
- **Observability:** health, command latency, bridge state, generation jobs, audio-system signals where available.

Every effectful command will carry an idempotency key, actor, mode, timestamp, requested action, execution result and readback. Assistant mode is the default.
