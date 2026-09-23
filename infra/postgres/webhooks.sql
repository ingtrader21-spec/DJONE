CREATE TABLE IF NOT EXISTS webhook_outbox (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(), event_type TEXT NOT NULL, subject_type TEXT,
 subject_id TEXT, correlation_id TEXT, payload JSONB NOT NULL DEFAULT '{}'::jsonb,
 status TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
 next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(), created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 delivered_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS webhook_outbox_pending_idx ON webhook_outbox(status,next_attempt_at);
