# Configuração do Supabase para o Agente Especialista em Tintas

Este documento descreve como configurar o Supabase como backend para o Agente Especialista em Tintas.

## 1. Criando o Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e faça login
2. Clique em "New Project"
3. Escolha sua organização
4. Defina um nome para o projeto (ex: "agente-tintas")
5. Crie uma senha segura para o banco de dados
6. Selecione uma região próxima ao seu público-alvo
7. Clique em "Create new project"

## 2. Configurando o Banco de Dados

1. Aguarde a criação do projeto (pode levar alguns minutos)
2. No dashboard do Supabase, vá para "SQL Editor"
3. Copie e cole o conteúdo do arquivo `supabase_setup.sql`
4. Execute o script clicando em "Run"

Este script criará:
- Todas as tabelas necessárias
- Índices para performance
- Triggers para atualização automática
- Políticas de segurança RLS
- Configurações iniciais do sistema

## 3. Obtendo as Chaves de API

1. No dashboard do Supabase, vá para "Settings" > "API"
2. Copie as seguintes informações:
   - **Project URL**: URL do seu projeto
   - **anon public**: Chave pública (para frontend)
   - **service_role**: Chave de serviço (para backend)

## 4. Configurando as Variáveis de Ambiente

1. Copie o arquivo `.env.example` para `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edite o arquivo `.env` com suas configurações:
   ```env
   SUPABASE_URL=https://seu-projeto.supabase.co
   SUPABASE_ANON_KEY=sua-chave-anonima-aqui
   SUPABASE_SERVICE_ROLE_KEY=sua-chave-service-role-aqui
   ```

## 5. Estrutura do Banco de Dados

### Tabelas Principais

#### `products`
Armazena informações dos produtos de tinta:
- `id`: UUID único
- `product_id`: ID do produto (único)
- `name`: Nome do produto
- `brand`: Marca
- `category`: Categoria
- `type`: Tipo de tinta
- `description`: Descrição
- `coverage`: Cobertura
- `drying_time`: Tempo de secagem
- `dilution`: Diluição
- `application_tools`: Ferramentas de aplicação
- `use_case`: Casos de uso
- `features`: Características
- `colors`: Cores disponíveis
- `packages`: Embalagens e preços (JSON)
- `active`: Produto ativo

#### `conversations`
Armazena conversas dos usuários:
- `id`: UUID único
- `session_id`: ID da sessão
- `platform`: Plataforma (web, whatsapp)
- `phone_number`: Número do WhatsApp (se aplicável)
- `user_id`: ID do usuário

#### `messages`
Armazena mensagens das conversas:
- `id`: UUID único
- `conversation_id`: Referência à conversa
- `message_type`: Tipo (user, agent)
- `content`: Conteúdo da mensagem
- `metadata`: Metadados (JSON)

#### `quotes`
Armazena orçamentos gerados:
- `id`: UUID único
- `conversation_id`: Referência à conversa
- `product_id`: Referência ao produto
- `area`: Área a ser pintada
- `coats`: Número de demãos
- `labor_included`: Inclui mão de obra
- `liters_needed`: Litros necessários
- `recommended_package`: Embalagem recomendada (JSON)
- `costs`: Custos detalhados (JSON)
- `status`: Status do orçamento

#### `knowledge_base`
Base de conhecimento para o sistema de aprendizado:
- `id`: UUID único
- `question`: Pergunta
- `answer`: Resposta
- `category`: Categoria
- `tags`: Tags
- `source`: Origem (manual, learned, catalog)
- `confidence_score`: Score de confiança
- `usage_count`: Contador de uso
- `embedding`: Vetor para busca semântica
- `active`: Conhecimento ativo

#### `feedback`
Feedback dos usuários:
- `id`: UUID único
- `conversation_id`: Referência à conversa
- `message_id`: Referência à mensagem
- `rating`: Avaliação (1-5)
- `comment`: Comentário
- `feedback_type`: Tipo de feedback

#### `system_config`
Configurações do sistema:
- `id`: UUID único
- `key`: Chave da configuração
- `value`: Valor (JSON)
- `description`: Descrição

#### `activity_logs`
Logs de atividade:
- `id`: UUID único
- `action`: Ação realizada
- `entity_type`: Tipo de entidade
- `entity_id`: ID da entidade
- `details`: Detalhes (JSON)
- `user_id`: ID do usuário
- `ip_address`: Endereço IP

## 6. Segurança (RLS - Row Level Security)

O banco está configurado com políticas de segurança que:
- Permitem leitura pública para produtos e conhecimento ativo
- Permitem inserção de conversas, mensagens e feedback
- Restringem operações administrativas a usuários autenticados
- Registram logs de atividade

## 7. Testando a Conexão

Para testar se a configuração está funcionando:

```python
from supabase_client import supabase_manager

# Verificar conexão
if supabase_manager.is_connected():
    print("✅ Conectado ao Supabase!")
    
    # Buscar estatísticas
    stats = supabase_manager.get_stats()
    print(f"Estatísticas: {stats}")
else:
    print("❌ Erro na conexão com Supabase")
```

## 8. Migrações e Backup

### Backup
Para fazer backup dos dados:
```sql
-- No SQL Editor do Supabase
SELECT * FROM products;
SELECT * FROM knowledge_base;
-- etc.
```

### Restauração
Para restaurar dados, use comandos INSERT no SQL Editor.

## 9. Monitoramento

O Supabase oferece:
- Dashboard com métricas em tempo real
- Logs de API
- Monitoramento de performance
- Alertas de uso

Acesse "Reports" no dashboard para visualizar essas informações.

## 10. Próximos Passos

Após configurar o Supabase:
1. Configure a Evolution API para WhatsApp
2. Atualize o backend Flask para usar o Supabase
3. Teste a integração completa
4. Configure monitoramento e alertas

## Troubleshooting

### Erro de Conexão
- Verifique se as URLs e chaves estão corretas
- Confirme se o projeto está ativo no Supabase
- Verifique a conectividade de rede

### Erro de Permissão
- Revise as políticas RLS
- Confirme se está usando a chave correta (anon vs service_role)
- Verifique se o usuário está autenticado quando necessário

### Performance
- Monitore o uso de recursos no dashboard
- Otimize queries complexas
- Considere índices adicionais se necessário
