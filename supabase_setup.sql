-- Configuração do banco de dados Supabase para o Agente Especialista em Tintas
-- Execute este script no SQL Editor do Supabase Dashboard

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    category VARCHAR(100) NOT NULL,
    type VARCHAR(100) NOT NULL,
    description TEXT,
    coverage VARCHAR(50),
    drying_time VARCHAR(100),
    dilution VARCHAR(100),
    application_tools TEXT[],
    use_case TEXT[],
    features TEXT[],
    colors TEXT[],
    packages JSONB,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de conversas/interações
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    platform VARCHAR(50) NOT NULL, -- 'web', 'whatsapp'
    phone_number VARCHAR(20), -- para WhatsApp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de mensagens
CREATE TABLE IF NOT EXISTS messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL, -- 'user', 'agent'
    content TEXT NOT NULL,
    metadata JSONB, -- informações extras como produtos mencionados, scores de busca, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de orçamentos
CREATE TABLE IF NOT EXISTS quotes (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    area DECIMAL(10,2) NOT NULL,
    coats INTEGER DEFAULT 2,
    labor_included BOOLEAN DEFAULT false,
    liters_needed DECIMAL(10,2),
    recommended_package JSONB,
    costs JSONB,
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'sent', 'accepted', 'rejected'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de conhecimento (para sistema de aprendizado)
CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    source VARCHAR(100), -- 'manual', 'learned', 'catalog'
    confidence_score DECIMAL(3,2) DEFAULT 1.0,
    usage_count INTEGER DEFAULT 0,
    last_used TIMESTAMP WITH TIME ZONE,
    embedding vector(1536), -- para busca semântica
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de feedback
CREATE TABLE IF NOT EXISTS feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    feedback_type VARCHAR(50), -- 'helpful', 'not_helpful', 'incorrect', 'suggestion'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de configurações do sistema
CREATE TABLE IF NOT EXISTS system_config (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de logs de atividade
CREATE TABLE IF NOT EXISTS activity_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50), -- 'product', 'conversation', 'quote', etc.
    entity_id UUID,
    details JSONB,
    user_id VARCHAR(255),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_active ON products(active);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_phone_number ON conversations(phone_number);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_quotes_conversation_id ON quotes(conversation_id);
CREATE INDEX IF NOT EXISTS idx_quotes_product_id ON quotes(product_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_category ON knowledge_base(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_base_active ON knowledge_base(active);
CREATE INDEX IF NOT EXISTS idx_feedback_conversation_id ON feedback(conversation_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_action ON activity_logs(action);
CREATE INDEX IF NOT EXISTS idx_activity_logs_created_at ON activity_logs(created_at);

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_quotes_updated_at BEFORE UPDATE ON quotes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir configurações iniciais do sistema
INSERT INTO system_config (key, value, description) VALUES
('whatsapp_webhook_url', '""', 'URL do webhook para receber mensagens do WhatsApp'),
('evolution_api_url', '""', 'URL base da Evolution API'),
('evolution_api_key', '""', 'Chave de API da Evolution API'),
('default_greeting', '"Olá! Sou seu especialista em tintas. Como posso ajudá-lo hoje?"', 'Mensagem de saudação padrão'),
('business_hours', '{"start": "08:00", "end": "18:00", "timezone": "America/Sao_Paulo"}', 'Horário de funcionamento'),
('auto_quote_enabled', 'true', 'Habilitar geração automática de orçamentos'),
('learning_enabled', 'true', 'Habilitar sistema de aprendizado')
ON CONFLICT (key) DO NOTHING;

-- Políticas de segurança RLS (Row Level Security)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_base ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE activity_logs ENABLE ROW LEVEL SECURITY;

-- Políticas básicas (ajustar conforme necessário)
CREATE POLICY "Enable read access for all users" ON products FOR SELECT USING (true);
CREATE POLICY "Enable insert access for authenticated users" ON products FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Enable update access for authenticated users" ON products FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Enable read access for all users" ON conversations FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON conversations FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON messages FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON messages FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON quotes FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON quotes FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for all users" ON knowledge_base FOR SELECT USING (active = true);
CREATE POLICY "Enable insert access for authenticated users" ON knowledge_base FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Enable insert access for all users" ON feedback FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable read access for authenticated users" ON system_config FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "Enable update access for authenticated users" ON system_config FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Enable insert access for all users" ON activity_logs FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable read access for authenticated users" ON activity_logs FOR SELECT USING (auth.role() = 'authenticated');
