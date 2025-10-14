
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    user_id TEXT,
    product_id TEXT,
    metadata JSONB
);

ALTER TABLE metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON metrics FOR SELECT USING (TRUE);
CREATE POLICY "Enable insert for authenticated users" ON metrics FOR INSERT WITH CHECK (auth.role() = 'authenticated');

