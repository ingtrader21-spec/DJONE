# DJONE

AI-assisted, self-hosted DJ workstation for Codestra's Ubuntu desktop.

## Architecture

Native host:
- Mixxx: low-latency DJ/audio engine and hardware access.

Docker:
- DJONE Control API
- DJ Agent orchestration
- Mixxx Bridge
- PostgreSQL
- Redis
- AI Remix service (ACE-Step integration)
- Stem separation service (Demucs integration)
- Observability

Flow:

User / AI Agent -> DJONE API -> policy & command ledger -> Mixxx Bridge -> Mixxx
                                     |
                                     +-> Remix -> Stems -> Library -> Mixxx

## Safety / control model

AI actions are explicit and auditable. Manual DJ controls always override automation.
Modes: Assistant, Copilot, Auto-DJ. Auto-DJ must be explicitly enabled.
No destructive library operation is enabled by default.

## Quick start

1. Copy `.env.example` to `.env`.
2. Run `./scripts/preflight.sh`.
3. Run `docker compose up -d --build`.
4. Check `http://localhost:8090/health`.
5. Configure the Mixxx bridge after Mixxx is installed natively.

See `docs/SETUP.md` and `docs/ARCHITECTURE.md`.
