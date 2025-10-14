# Agente Especialista em Tintas e Pisos

Este projeto é um sistema multi-agente projetado para fornecer conhecimento especializado em tintas e revestimentos de piso. O sistema utiliza processamento de linguagem natural (PNL) avançado, busca semântica e uma arquitetura de múltiplos agentes para fornecer respostas precisas e contextuais às consultas dos usuários. A interação do usuário é facilitada por meio de interfaces de site e WhatsApp.

## Visão Geral do Sistema

O sistema é composto pelos seguintes componentes principais:

- **Frontend:** Uma interface de usuário baseada em React que permite aos usuários interagir com os agentes, gerenciar produtos e visualizar análises.
- **Backend:** Uma API Flask que lida com a lógica de negócios, processamento de linguagem natural e comunicação com o banco de dados e serviços externos.
- **Banco de Dados:** Supabase é usado para gerenciamento de banco de dados, autenticação e armazenamento de arquivos.
- **Agentes de IA:**
    - **Agentes Especializados:** Agentes focados em domínios de conhecimento específicos (por exemplo, tintas, revestimentos de piso).
    - **Agente Orquestrador:** Roteia as consultas dos usuários para o agente especializado apropriado.
    - **Agente Revisor:** Revisa e refina as respostas do agente para precisão e clareza.
- **Base de Conhecimento:** Uma coleção de documentos, catálogos de produtos e outros dados que os agentes usam para responder às perguntas.

## Recursos

- **Sistema Multi-Agente:** Arquitetura expansível que suporta múltiplos agentes especializados.
- **Busca Semântica:** Permite que os usuários pesquisem produtos e informações usando linguagem natural.
- **Gerenciamento da Base de Conhecimento:** Ferramentas para upload, processamento e edição da base de conhecimento.
- **Gerenciamento de Prompts:** Sistema para gerenciar e versionar os prompts usados pelos agentes de IA.
- **Rastreamento de Métricas:** Rastreamento abrangente de interações do usuário, desempenho do agente e outras métricas importantes.
- **Conformidade com LGPD:** Recursos para garantir a privacidade e proteção de dados do usuário.
- **Integração com WhatsApp:** Permite que os usuários interajam com o sistema por meio do WhatsApp.
- **Painel de Análise:** Visualização de métricas e insights importantes.

## Contexto Técnico

- **Frontend:** React, Vite, Tailwind CSS
- **Backend:** Flask, Python
- **Banco de Dados:** Supabase (PostgreSQL)
- **IA e PNL:** OpenAI API, spaCy, scikit-learn
- **Comunicação em Tempo Real:** WebSockets (via Supabase Realtime)
- **Integração com WhatsApp:** Evolution API

## Primeiros Passos

### Pré-requisitos

- Python 3.11 ou superior
- Node.js 22.13.0 ou superior
- Acesso a uma instância do Supabase
- Acesso à API da OpenAI
- Acesso à Evolution API para integração com o WhatsApp

### Instalação

1. **Clone o repositório:**

   ```bash
   git clone <url-do-repositorio>
   cd agente-tintas
   ```

2. **Configure o Backend:**

   - Navegue até o diretório do backend:
     ```bash
     cd backend
     ```
   - Crie e ative um ambiente virtual:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Instale as dependências do Python:
     ```bash
     pip install -r requirements.txt
     ```
   - Configure as variáveis de ambiente:
     - Copie o arquivo `.env.example` para `.env`.
     - Preencha as variáveis de ambiente necessárias (credenciais do Supabase, chave da API da OpenAI, etc.).

3. **Configure o Frontend:**

   - Navegue até o diretório raiz do projeto.
   - Instale as dependências do Node.js:
     ```bash
     npm install --legacy-peer-deps
     ```

### Executando a Aplicação

1. **Inicie o Backend:**

   ```bash
   cd backend
   source venv/bin/activate
   python3 app.py
   ```

2. **Inicie o Frontend:**

   ```bash
   npm run dev
   ```

   A aplicação estará disponível em `http://localhost:5173`.

## Estrutura do Projeto

```
/agente-tintas
|-- /backend
|   |-- app.py                  # Aplicação principal do Flask
|   |-- requirements.txt        # Dependências do Python
|   |-- supabase_client.py      # Cliente para interagir com o Supabase
|   |-- evolution_api_client.py # Cliente para interagir com a Evolution API
|   |-- ...                     # Outros módulos do backend
|-- /src
|   |-- App.jsx                 # Componente principal do React
|   |-- /components             # Componentes React
|   |-- ...                     # Outros arquivos do frontend
|-- package.json                # Dependências do Node.js
|-- README.md                   # Este arquivo
```

