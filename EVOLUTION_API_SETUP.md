# Configuração da Evolution API para WhatsApp

Este documento descreve como configurar e integrar a Evolution API com o Agente Especialista em Tintas.

## 1. Instalação da Evolution API

### Opção 1: Docker (Recomendado)

```bash
# Baixar o docker-compose da Evolution API v2.3.4
wget https://github.com/EvolutionAPI/evolution-api/releases/download/2.3.4/docker-compose.yml

# Configurar variáveis de ambiente
cp .env.example .env

# Editar o arquivo .env com suas configurações
nano .env

# Iniciar os serviços
docker-compose up -d
```

### Opção 2: Instalação Manual

```bash
# Clonar o repositório
git clone https://github.com/EvolutionAPI/evolution-api.git
cd evolution-api

# Checkout para a versão 2.3.4
git checkout 2.3.4

# Instalar dependências
npm install

# Configurar ambiente
cp .env.example .env

# Iniciar a aplicação
npm run start:prod
```

## 2. Configuração Básica

### Arquivo .env da Evolution API

```env
# Configurações do servidor
SERVER_TYPE=http
SERVER_PORT=8080
SERVER_URL=http://localhost:8080

# Configurações do banco de dados
DATABASE_ENABLED=true
DATABASE_CONNECTION_URI=postgresql://user:password@localhost:5432/evolution
DATABASE_CONNECTION_CLIENT_NAME=evolution_api

# Configurações de autenticação
AUTHENTICATION_TYPE=apikey
AUTHENTICATION_API_KEY=sua-chave-api-aqui
AUTHENTICATION_EXPOSE_IN_FETCH_INSTANCES=true

# Configurações de webhook
WEBHOOK_GLOBAL_URL=http://seu-servidor.com/webhook/evolution
WEBHOOK_GLOBAL_ENABLED=true
WEBHOOK_GLOBAL_WEBHOOK_BY_EVENTS=false

# Eventos do webhook
WEBHOOK_EVENTS_APPLICATION_STARTUP=false
WEBHOOK_EVENTS_QRCODE_UPDATED=true
WEBHOOK_EVENTS_MESSAGES_SET=false
WEBHOOK_EVENTS_MESSAGES_UPSERT=true
WEBHOOK_EVENTS_MESSAGES_UPDATE=true
WEBHOOK_EVENTS_MESSAGES_DELETE=false
WEBHOOK_EVENTS_SEND_MESSAGE=true
WEBHOOK_EVENTS_CONTACTS_SET=false
WEBHOOK_EVENTS_CONTACTS_UPSERT=false
WEBHOOK_EVENTS_CONTACTS_UPDATE=false
WEBHOOK_EVENTS_PRESENCE_UPDATE=false
WEBHOOK_EVENTS_CHATS_SET=false
WEBHOOK_EVENTS_CHATS_UPDATE=false
WEBHOOK_EVENTS_CHATS_UPSERT=false
WEBHOOK_EVENTS_CHATS_DELETE=false
WEBHOOK_EVENTS_GROUPS_UPSERT=false
WEBHOOK_EVENTS_GROUPS_UPDATE=false
WEBHOOK_EVENTS_GROUP_PARTICIPANTS_UPDATE=false
WEBHOOK_EVENTS_CONNECTION_UPDATE=true
WEBHOOK_EVENTS_LABELS_EDIT=false
WEBHOOK_EVENTS_LABELS_ASSOCIATION=false
WEBHOOK_EVENTS_CALL=false
WEBHOOK_EVENTS_NEW_JWT=false
WEBHOOK_EVENTS_TYPEBOT_START=false
WEBHOOK_EVENTS_TYPEBOT_CHANGE_STATUS=false

# Configurações de logs
LOG_LEVEL=ERROR
LOG_COLOR=true
LOG_BAILEYS=error
```

## 3. Configuração do Agente de Tintas

### Variáveis de Ambiente (.env)

```env
# Evolution API
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-api-aqui
EVOLUTION_INSTANCE_NAME=agente-tintas

# Webhook URL (onde a Evolution API enviará os eventos)
WEBHOOK_URL=http://seu-servidor.com/webhook/evolution
```

## 4. Criando uma Instância

### Via API

```bash
curl -X POST http://localhost:8080/instance/create \
  -H "Content-Type: application/json" \
  -H "apikey: sua-chave-api-aqui" \
  -d '{
    "instanceName": "agente-tintas",
    "qrcode": true,
    "integration": "WHATSAPP-BAILEYS",
    "webhook": {
      "url": "http://seu-servidor.com/webhook/evolution",
      "events": [
        "QRCODE_UPDATED",
        "CONNECTION_UPDATE",
        "MESSAGES_UPSERT",
        "MESSAGES_UPDATE",
        "SEND_MESSAGE"
      ]
    }
  }'
```

### Via Interface Web

1. Acesse `http://localhost:8080` no navegador
2. Use a chave API para autenticar
3. Clique em "Create Instance"
4. Preencha os dados da instância
5. Configure o webhook

## 5. Conectando ao WhatsApp

### Método 1: QR Code (Recomendado para testes)

1. Após criar a instância, um QR Code será gerado
2. Abra o WhatsApp no celular
3. Vá em "Dispositivos conectados"
4. Escaneie o QR Code
5. A instância ficará conectada

### Método 2: WhatsApp Business API (Produção)

Para usar a API oficial do WhatsApp Business:

1. Crie uma conta no Facebook Business Manager
2. Configure um app no Facebook Developers
3. Obtenha aprovação para WhatsApp Business API
4. Configure a instância com token permanente:

```json
{
  "instanceName": "agente-tintas-business",
  "token": "seu-token-permanente",
  "number": "seu-numero-id",
  "businessId": "seu-business-id",
  "qrcode": false,
  "integration": "WHATSAPP-BUSINESS"
}
```

## 6. Configuração do Webhook

### Endpoint do Webhook

O agente de tintas deve expor um endpoint para receber webhooks:

```
POST /webhook/evolution
```

### Estrutura do Webhook

```json
{
  "event": "MESSAGES_UPSERT",
  "instance": "agente-tintas",
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false,
      "id": "message-id"
    },
    "message": {
      "conversation": "Olá, preciso de uma tinta para quarto"
    },
    "messageType": "conversation",
    "messageTimestamp": 1640995200
  }
}
```

## 7. Testando a Integração

### Verificar Status da Instância

```bash
curl -X GET http://localhost:8080/instance/connectionState/agente-tintas \
  -H "apikey: sua-chave-api-aqui"
```

### Enviar Mensagem de Teste

```bash
curl -X POST http://localhost:8080/message/sendText/agente-tintas \
  -H "Content-Type: application/json" \
  -H "apikey: sua-chave-api-aqui" \
  -d '{
    "number": "5511999999999",
    "text": "Olá! Sou seu especialista em tintas. Como posso ajudá-lo?"
  }'
```

### Verificar Webhook

```bash
curl -X GET http://localhost:8080/webhook/find/agente-tintas \
  -H "apikey: sua-chave-api-aqui"
```

## 8. Funcionalidades Implementadas

### Processamento de Mensagens

- ✅ Recebimento de mensagens via webhook
- ✅ Identificação do remetente
- ✅ Extração do conteúdo da mensagem
- ✅ Geração de resposta automática
- ✅ Envio de resposta

### Tipos de Mensagem Suportados

- ✅ Texto simples
- ✅ Mensagens com botões
- ✅ Listas de opções
- ✅ Imagens com legenda
- ✅ Documentos

### Recursos do Agente

- ✅ Busca semântica de produtos
- ✅ Geração de orçamentos
- ✅ Cálculo de quantidade de tinta
- ✅ Recomendações técnicas
- ✅ Histórico de conversas
- ✅ Logs de atividade

## 9. Monitoramento e Logs

### Logs da Evolution API

```bash
# Ver logs em tempo real
docker-compose logs -f evolution-api

# Ver logs específicos de uma instância
grep "agente-tintas" /var/log/evolution-api.log
```

### Métricas do Agente

O agente coleta métricas como:
- Número de conversas ativas
- Mensagens processadas
- Orçamentos gerados
- Produtos mais consultados
- Tempo de resposta

### Dashboard de Monitoramento

Acesse as estatísticas em:
- Evolution API: `http://localhost:8080/manager`
- Agente: Interface web do React

## 10. Troubleshooting

### Problemas Comuns

**Instância não conecta:**
- Verifique se o QR Code foi escaneado
- Confirme se o WhatsApp está ativo no celular
- Verifique logs da Evolution API

**Webhook não funciona:**
- Confirme se a URL está acessível
- Verifique se o endpoint está respondendo
- Teste com ngrok para desenvolvimento local

**Mensagens não são enviadas:**
- Verifique se a instância está conectada
- Confirme o formato do número de telefone
- Verifique logs de erro

### Comandos Úteis

```bash
# Reiniciar instância
curl -X POST http://localhost:8080/instance/restart/agente-tintas \
  -H "apikey: sua-chave-api-aqui"

# Desconectar instância
curl -X DELETE http://localhost:8080/instance/logout/agente-tintas \
  -H "apikey: sua-chave-api-aqui"

# Listar todas as instâncias
curl -X GET http://localhost:8080/instance/fetchInstances \
  -H "apikey: sua-chave-api-aqui"
```

## 11. Segurança

### Boas Práticas

- Use HTTPS em produção
- Mantenha a chave API segura
- Configure firewall para limitar acesso
- Use autenticação JWT se disponível
- Monitore logs de acesso

### Validação de Webhook

```python
# Validar origem do webhook
def validate_webhook(request):
    api_key = request.headers.get('apikey')
    return api_key == os.getenv('EVOLUTION_API_KEY')
```

## 12. Próximos Passos

Após configurar a Evolution API:

1. ✅ Teste a conexão básica
2. ✅ Configure o webhook
3. ✅ Teste envio e recebimento de mensagens
4. ✅ Integre com o sistema de busca semântica
5. ✅ Configure logs e monitoramento
6. ⏳ Deploy em produção
7. ⏳ Configure domínio personalizado
8. ⏳ Implemente backup e recuperação

## 13. Recursos Adicionais

- [Documentação oficial da Evolution API](https://doc.evolution-api.com/)
- [GitHub da Evolution API](https://github.com/EvolutionAPI/evolution-api)
- [Comunidade no Discord](https://discord.gg/evolution-api)
- [Exemplos de integração](https://github.com/EvolutionAPI/evolution-api/tree/main/examples)
