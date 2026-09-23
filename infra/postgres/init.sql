CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE TABLE IF NOT EXISTS dj_commands (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), idempotency_key TEXT UNIQUE NOT NULL,
  actor TEXT NOT NULL DEFAULT 'api', mode TEXT NOT NULL, action TEXT NOT NULL, deck INTEGER,
  value_json JSONB, status TEXT NOT NULL, accepted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  executed_at TIMESTAMPTZ, result_json JSONB, readback_json JSONB
);
CREATE INDEX IF NOT EXISTS dj_commands_status_idx ON dj_commands(status);
CREATE TABLE IF NOT EXISTS music_tracks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(), sha256 TEXT UNIQUE NOT NULL, path TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'local', provenance TEXT, status TEXT NOT NULL DEFAULT 'registered',
  duration_seconds DOUBLE PRECISION, bpm DOUBLE PRECISION, musical_key TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS deck_state (
  deck SMALLINT PRIMARY KEY CHECK(deck BETWEEN 1 AND 4), connected BOOLEAN NOT NULL DEFAULT false,
  track_id UUID REFERENCES music_tracks(id), play BOOLEAN, bpm DOUBLE PRECISION, musical_key TEXT,
  observed_at TIMESTAMPTZ
);
INSERT INTO deck_state(deck) VALUES(1),(2),(3),(4) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS safety_state (
  singleton BOOLEAN PRIMARY KEY DEFAULT true CHECK(singleton), execution_enabled BOOLEAN NOT NULL DEFAULT false,
  emergency_stop BOOLEAN NOT NULL DEFAULT false, manual_override BOOLEAN NOT NULL DEFAULT true,
  certified BOOLEAN NOT NULL DEFAULT false, updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
INSERT INTO safety_state(singleton) VALUES(true) ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS dj_events (
  id BIGSERIAL PRIMARY KEY, kind TEXT NOT NULL, payload JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
