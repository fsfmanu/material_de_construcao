'''
# Guia de Integração: Agente de Tintas com Supabase e Evolution API

**Versão:** 1.0
**Data:** 29 de Setembro de 2025

## 1. Visão Geral

Este documento detalha a arquitetura e os passos necessários para configurar e executar o **Agente Especialista em Tintas** com a integração completa do backend **Supabase** e da **Evolution API** para comunicação via WhatsApp.

A integração transforma o agente de uma aplicação local para um sistema robusto e escalável, com persistência de dados, autenticação, e capacidade de comunicação em tempo real.

## 2. Arquitetura do Sistema

O sistema é composto por três componentes principais:

1.  **Frontend (React):** A interface do usuário construída com React e Vite. É responsável por toda a interação com o usuário, incluindo o chat, a calculadora, o gerenciamento de produtos e a visualização de analytics.
2.  **Backend (Flask):** O cérebro do sistema. Uma API construída com Flask que orquestra todas as operações, incluindo:
    *   Busca semântica na base de conhecimento.
    *   Comunicação com o Supabase para persistência de dados.
    *   Comunicação com a Evolution API para envio e recebimento de mensagens do WhatsApp.
    *   Lógica de negócios para orçamentos, cálculos e recomendações.
3.  **Banco de Dados e Backend as a Service (Supabase):** A plataforma que fornece o banco de dados PostgreSQL, autenticação, armazenamento e APIs automáticas. É usada para armazenar todas as informações do agente.
4.  **Gateway de WhatsApp (Evolution API):** A ponte entre o nosso agente e o WhatsApp. Ela gerencia a conexão, o envio e o recebimento de mensagens.

### Fluxo de Dados

-   **Chat Web:** `React Frontend` -> `Flask Backend` -> `Supabase` (para salvar conversa) -> `Flask Backend` -> `React Frontend`.
-   **Chat WhatsApp:** `Usuário WhatsApp` -> `Evolution API` -> `Webhook Flask` -> `Supabase` (para salvar conversa) -> `Flask Backend` -> `Evolution API` -> `Usuário WhatsApp`.

## 3. Configuração do Ambiente

Para executar o projeto, você precisará configurar as variáveis de ambiente. Renomeie o arquivo `.env.example` no diretório `backend` para `.env` e preencha as seguintes variáveis:

```sh
# /home/ubuntu/agente-tintas/backend/.env

# --- Configuração do Supabase ---
# Obtenha no painel do seu projeto no Supabase (Project Settings > API)
SUPABASE_URL="SUA_URL_DO_SUPABASE"
SUPABASE_KEY="SUA_CHAVE_ANON_DO_SUPABASE"
SUPABASE_SERVICE_KEY="SUA_CHAVE_SERVICE_ROLE_DO_SUPABASE"

# --- Configuração da Evolution API ---
# URL da sua instância da Evolution API
EVOLUTION_API_URL="http://localhost:8080"
# Nome da instância que você criou na Evolution API
EVOLUTION_API_INSTANCE="default-instance"
# Chave de API Global da Evolution API (definida na configuração da sua instância)
EVOLUTION_API_KEY="SUA_CHAVE_GLOBAL_DA_EVOLUTION_API"

# --- Configuração do Servidor ---
# URL pública do seu backend Flask para o webhook da Evolution API
# Use uma ferramenta como ngrok para expor seu ambiente local publicamente durante o desenvolvimento
# Ex: https://seu-dominio-publico.ngrok.io
FLASK_SERVER_URL="SUA_URL_PUBLICA_DO_BACKEND"
```

**IMPORTANTE:** A `FLASK_SERVER_URL` é crucial para que a Evolution API possa enviar eventos de webhook para o seu backend.

## 4. Executando o Sistema

Siga os passos abaixo para iniciar todos os componentes do sistema.

### Passo 1: Iniciar o Backend Flask

Abra um terminal e execute:

```bash
# Navegue até o diretório do backend
cd /home/ubuntu/agente-tintas/backend

# Instale as dependências (se ainda não o fez)
pip3 install -r requirements.txt

# Inicie o servidor
python3 app.py
```

O servidor Flask estará rodando em `http://0.0.0.0:5000`.

### Passo 2: Iniciar o Frontend React

Abra um segundo terminal e execute:

```bash
# Navegue até o diretório do frontend
cd /home/ubuntu/agente-tintas

# Instale as dependências (se ainda não o fez)
npm install

# Inicie o servidor de desenvolvimento
npm run dev -- --host
```

O frontend estará acessível em `http://<seu-ip-local>:5173`.

### Passo 3: Configurar a Evolution API

1.  Siga a documentação oficial da Evolution API para instalá-la e iniciá-la.
2.  Crie uma instância (ex: `default-instance`).
3.  Conecte a instância ao seu WhatsApp escaneando o QR Code.
4.  Configure o **Webhook Global de Mensagens** na Evolution API para apontar para o seu backend:
    *   **URL do Webhook:** `SUA_URL_PUBLICA_DO_BACKEND/webhook/evolution`

## 5. Testes Finais

Após iniciar todos os serviços, realize os seguintes testes:

1.  **Conexão com a API:**
    *   Acesse o frontend React. O status "IA Avançada" deve estar verde.
    *   Navegue até a aba "Analytics". O status do Supabase deve ser "Conectado" e o da Evolution API "Configurada".

2.  **Chat Web e Persistência:**
    *   Envie uma mensagem pelo chat no frontend.
    *   Verifique na aba "Analytics" se o número de conversas e mensagens aumentou.
    *   Verifique no seu painel do Supabase se a conversa e as mensagens foram salvas nas tabelas `conversations` e `messages`.

3.  **Integração com WhatsApp:**
    *   Envie uma mensagem de um número de telefone para o WhatsApp conectado à Evolution API.
    *   O agente deve responder à mensagem.
    *   Verifique no painel do Supabase se a nova conversa (com `platform: 'whatsapp'`) foi criada e se as mensagens foram registradas.

4.  **Gerenciamento de Produtos:**
    *   Vá para a aba "Admin". Adicione, edite ou remova um produto.
    *   Verifique se as alterações foram refletidas na tabela `products` do Supabase.

5.  **Orçamentos:**
    *   Solicite um orçamento pelo chat do WhatsApp ou pela aba "Produtos" no frontend.
    *   Verifique se o orçamento foi gerado corretamente e salvo na tabela `quotes` do Supabase.

## 6. Conclusão

Este guia fornece as instruções essenciais para a configuração e operação do Agente Especialista em Tintas integrado. Com o Supabase e a Evolution API, o sistema está preparado para escalar e oferecer uma experiência robusta e persistente para os usuários, tanto na web quanto no WhatsApp.
'''
