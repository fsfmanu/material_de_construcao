-- Script SQL para adicionar gerenciamento de prompts ao Supabase
-- Execute este script após o supabase_setup.sql principal

-- Tabela para armazenar configurações de prompts dos agentes
CREATE TABLE IF NOT EXISTS agent_prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_type VARCHAR(50) NOT NULL, -- 'tintas', 'pisos', 'orquestrador', 'revisor'
    prompt_type VARCHAR(50) NOT NULL, -- 'initial_greeting', 'product_recommendation', 'error_message', etc.
    prompt_text TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_agent_prompts_type ON agent_prompts(agent_type);
CREATE INDEX IF NOT EXISTS idx_agent_prompts_active ON agent_prompts(is_active);
CREATE INDEX IF NOT EXISTS idx_agent_prompts_type_prompt ON agent_prompts(agent_type, prompt_type);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_agent_prompts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_prompts_updated_at_trigger
    BEFORE UPDATE ON agent_prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_prompts_updated_at();

-- Inserir prompts iniciais para o agente de tintas
INSERT INTO agent_prompts (agent_type, prompt_type, prompt_text, description) VALUES
(
    'tintas',
    'initial_greeting',
    'Olá! Sou seu especialista em tintas com 20 anos de experiência. Posso ajudá-lo com recomendações de produtos, cálculos de quantidade, orçamentos e solução de problemas de pintura.',
    'Saudação inicial do agente de tintas'
),
(
    'tintas',
    'product_recommendation_intro',
    'Encontrei {count} produto(s) relevante(s) para sua consulta:',
    'Introdução para recomendações de produtos'
),
(
    'tintas',
    'budget_request',
    'Para elaborar um orçamento preciso, preciso saber:
1. Tipo de projeto (residencial/comercial/industrial)
2. Superfície a pintar (parede, madeira, metal, etc.)
3. Área em m²
4. Condições do ambiente (interno/externo, umidade)
5. Acabamento desejado (fosco, acetinado, brilhante)

Você pode me fornecer essas informações?',
    'Solicitação de informações para orçamento'
),
(
    'tintas',
    'paint_problem_diagnosis',
    'Problemas de descascamento geralmente indicam:
1. Superfície mal preparada (80% dos casos)
2. Presença de umidade
3. Incompatibilidade química entre produtos

**Recomendo:** Remoção completa das camadas soltas, tratamento da umidade na fonte e aplicação de primer adequado.',
    'Diagnóstico para problemas de pintura'
),
(
    'tintas',
    'calculation_help',
    'Para calcular a tinta necessária:
- Área Total = (Largura × Altura × Paredes) - Vãos
- Litros = Área ÷ Rendimento ÷ Demãos + 10% para perdas

Qual a área que você precisa pintar?',
    'Ajuda para cálculos de quantidade'
),
(
    'tintas',
    'no_results_found',
    'Não encontrei produtos específicos para sua consulta, mas posso ajudá-lo com:

🎨 **Recomendações de produtos**
📊 **Cálculo de materiais**
🔧 **Solução de problemas**
💰 **Orçamentos personalizados**
🌈 **Escolha de cores e sistemas de pintura**

Qual sua necessidade específica?',
    'Resposta quando não há resultados na busca'
),
(
    'tintas',
    'error_message',
    'Desculpe, ocorreu um erro técnico. Por favor, tente novamente ou reformule sua pergunta. Se o problema persistir, entre em contato com nosso suporte.',
    'Mensagem de erro genérica'
);

-- Inserir prompts iniciais para o agente orquestrador (será usado futuramente)
INSERT INTO agent_prompts (agent_type, prompt_type, prompt_text, description) VALUES
(
    'orquestrador',
    'initial_greeting',
    'Olá! Sou seu assistente especializado em materiais de construção. Posso ajudá-lo com tintas, pisos, revestimentos e muito mais. Como posso ajudá-lo hoje?',
    'Saudação inicial do agente orquestrador'
),
(
    'orquestrador',
    'routing_message',
    'Vou conectá-lo com nosso especialista em {specialty} para melhor atendê-lo.',
    'Mensagem ao rotear para especialista'
);

-- Inserir prompts iniciais para o agente revisor (será usado futuramente)
INSERT INTO agent_prompts (agent_type, prompt_type, prompt_text, description) VALUES
(
    'revisor',
    'quality_check_intro',
    'Revisando a resposta para garantir precisão e clareza...',
    'Introdução do processo de revisão'
);

-- Política RLS (Row Level Security) para agent_prompts
ALTER TABLE agent_prompts ENABLE ROW LEVEL SECURITY;

-- Política para permitir leitura para usuários autenticados
CREATE POLICY "Allow read access to agent_prompts" ON agent_prompts
    FOR SELECT USING (true);

-- Política para permitir escrita apenas para usuários autenticados (administradores)
CREATE POLICY "Allow write access to agent_prompts for authenticated users" ON agent_prompts
    FOR ALL USING (auth.role() = 'authenticated');

-- Comentários nas tabelas e colunas
COMMENT ON TABLE agent_prompts IS 'Armazena os prompts e frases configuráveis dos agentes especialistas';
COMMENT ON COLUMN agent_prompts.agent_type IS 'Tipo do agente: tintas, pisos, orquestrador, revisor';
COMMENT ON COLUMN agent_prompts.prompt_type IS 'Tipo do prompt: initial_greeting, product_recommendation, etc.';
COMMENT ON COLUMN agent_prompts.prompt_text IS 'Texto do prompt que será usado pelo agente';
COMMENT ON COLUMN agent_prompts.description IS 'Descrição do propósito do prompt';
COMMENT ON COLUMN agent_prompts.is_active IS 'Indica se o prompt está ativo e deve ser usado';
