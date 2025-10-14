
CREATE TABLE IF NOT EXISTS user_consent (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL,
    consent_type TEXT NOT NULL,
    granted BOOLEAN NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB,
    UNIQUE (user_id, consent_type)
);

ALTER TABLE user_consent ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable read access for all users" ON user_consent FOR SELECT USING (TRUE);
CREATE POLICY "Enable insert for authenticated users" ON user_consent FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update for authenticated users" ON user_consent FOR UPDATE USING (auth.role() = 'authenticated');

