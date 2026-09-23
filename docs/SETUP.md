# Codestra's Ubuntu Setup

## Host responsibilities
Mixxx stays native on Ubuntu for audio, USB/MIDI/HID and low latency. DJONE supporting services run in Docker.

## Preflight
Required: git, Docker Engine with Compose v2, curl. Optional for AI acceleration: NVIDIA GPU, working driver and NVIDIA Container Toolkit.

Run:
```bash
./scripts/preflight.sh
```

## Bootstrap
```bash
cp .env.example .env
docker compose up -d --build
curl -fsS http://localhost:8090/health
```

## AI remix
ACE-Step and Demucs are intentionally separate optional services. GPU/VRAM must be detected before selecting model/runtime profiles. Do not route real-time Mixxx audio through containers.

## Next implementation gates
1. Mixxx control adapter + readback.
2. Durable command ledger/idempotency.
3. Agent policy modes and emergency/manual override.
4. Library ingestion/metadata.
5. Demucs stems.
6. ACE-Step remix generation.
7. Recording/streaming pipeline.
8. Metrics and dashboard.
