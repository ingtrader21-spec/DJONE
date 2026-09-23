# Endpoint Implementation Matrix

| Area | Endpoint | Stage |
|---|---|---|
| System | GET /health | implemented |
| System | GET /ready | implemented |
| System | GET /v1/capabilities | implemented |
| Decks | GET /v1/decks | next |
| Decks | GET /v1/decks/{deck} | next |
| Commands | POST /v1/commands | foundation implemented; durable execution pending |
| Commands | GET /v1/commands/{idempotency_key} | foundation implemented |
| Agent | POST /v1/agent/plan | next |
| Agent | POST /v1/agent/execute | gated |
| Remix | GET /v1/remix/capabilities | implemented |
| Remix | POST /v1/remix/jobs | implemented |
| Remix | GET /v1/remix/jobs | next |
| Remix | GET /v1/remix/jobs/{job_id} | implemented |
| Library | GET/POST /v1/library/tracks | next |
| Sessions | GET/POST /v1/sessions | next |
| Sessions | GET /v1/sessions/{id}/events | next |
| Safety | GET /v1/safety/status | next |
| Safety | POST /v1/safety/emergency-stop | next |
| Safety | POST /v1/safety/resume | next |

## Gate
No endpoint may report a Mixxx effect as completed without observed-state readback.
