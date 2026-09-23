CREATE TABLE IF NOT EXISTS dj_commands (
  id UUID PRIMARY KEY,
  idempotency_key TEXT UNIQUE NOT NULL,
  actor TEXT NOT NULL DEFAULT 'api',
  mode TEXT NOT NULL,
  action TEXT NOT NULL,
  deck INTEGER,
  value_json JSONB,
  status TEXT NOT NULL,
  accepted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  executed_at TIMESTAMPTZ,
  result_json JSONB,
  readback_json JSONB
);
CREATE INDEX IF NOT EXISTS dj_commands_status_idx ON dj_commands(status);
