import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { MessageCircle, Smartphone, Settings, Zap, Users, BarChart3 } from 'lucide-react'

const WhatsAppIntegration = () => {
  const [webhookUrl, setWebhookUrl] = useState('')
  const [apiToken, setApiToken] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState([])

  // Dados simulados de mensagens do WhatsApp
  const mockMessages = [
    {
      id: 1,
      from: '+5511999999999',
      message: 'Oi, preciso de uma tinta para pintar minha sala',
      timestamp: new Date().toISOString(),
      status: 'received',
      response: 'Olá! Para sua sala, recomendo uma tinta acrílica premium como Coral Master ou Suvinil Diamante. Qual o tamanho da sala?'
    },
    {
      id: 2,
      from: '+5511888888888',
      message: 'Quanto custa para pintar uma casa de 120m²?',
      timestamp: new Date().toISOString(),
      status: 'received',
      response: 'Para um orçamento preciso de 120m², preciso saber: número de cômodos, altura das paredes e tipo de tinta desejada. Posso fazer um cálculo estimativo?'
    },
    {
      id: 3,
      from: '+5511777777777',
      message: 'Minha parede está com mofo, que tinta usar?',
      timestamp: new Date().toISOString(),
      status: 'received',
      response: 'Para paredes com mofo, recomendo: 1) Limpeza com hipoclorito, 2) Primer antifúngico, 3) Tinta com ação antimicrobiana como Coral Super Lavável.'
    }
  ]

  const connectWhatsApp = () => {
    if (webhookUrl && apiToken) {
      setIsConnected(true)
      setMessages(mockMessages)
    }
  }

  const disconnectWhatsApp = () => {
    setIsConnected(false)
    setMessages([])
  }

  const stats = {
    totalMessages: messages.length,
    responseRate: '98%',
    avgResponseTime: '2.3s',
    satisfaction: '4.8/5'
  }

  return (
    <div className="space-y-6">
      {/* Status da Conexão */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Status da Integração WhatsApp
          </CardTitle>
          <CardDescription>
            Configure e monitore a conexão com o WhatsApp Business API
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4 mb-4">
            <Badge variant={isConnected ? "default" : "secondary"} className="flex items-center gap-1">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
              {isConnected ? 'Conectado' : 'Desconectado'}
            </Badge>
            {isConnected && (
              <span className="text-sm text-gray-600">
                Última sincronização: {new Date().toLocaleString('pt-BR')}
              </span>
            )}
          </div>

          {!isConnected ? (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Webhook URL</label>
                <Input
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  placeholder="https://api.whatsapp.com/webhook"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">API Token</label>
                <Input
                  type="password"
                  value={apiToken}
                  onChange={(e) => setApiToken(e.target.value)}
                  placeholder="Seu token da WhatsApp Business API"
                />
              </div>
              <Button onClick={connectWhatsApp} className="w-full">
                <Smartphone className="h-4 w-4 mr-2" />
                Conectar WhatsApp
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{stats.totalMessages}</p>
                  <p className="text-sm text-blue-800">Mensagens</p>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">{stats.responseRate}</p>
                  <p className="text-sm text-green-800">Taxa Resposta</p>
                </div>
                <div className="text-center p-3 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">{stats.avgResponseTime}</p>
                  <p className="text-sm text-orange-800">Tempo Médio</p>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">{stats.satisfaction}</p>
                  <p className="text-sm text-purple-800">Satisfação</p>
                </div>
              </div>
              <Button onClick={disconnectWhatsApp} variant="outline" className="w-full">
                Desconectar
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configurações do Bot */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Configurações do Bot
          </CardTitle>
          <CardDescription>
            Personalize o comportamento do agente no WhatsApp
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Mensagem de Boas-vindas</label>
            <Textarea
              defaultValue="Olá! 👋 Sou seu especialista em tintas com 20 anos de experiência. Como posso ajudá-lo hoje? Posso auxiliar com recomendações de produtos, cálculos de materiais e orçamentos!"
              rows={3}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Mensagem de Horário Comercial</label>
            <Textarea
              defaultValue="Obrigado por entrar em contato! Nosso horário de atendimento é de segunda a sexta, das 8h às 18h. Deixe sua mensagem que responderemos assim que possível."
              rows={2}
            />
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Tempo de Resposta (segundos)</label>
              <Input type="number" defaultValue="2" min="1" max="10" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Máximo de Mensagens por Conversa</label>
              <Input type="number" defaultValue="50" min="10" max="100" />
            </div>
          </div>
          <Button className="w-full">
            <Settings className="h-4 w-4 mr-2" />
            Salvar Configurações
          </Button>
        </CardContent>
      </Card>

      {/* Mensagens Recentes */}
      {isConnected && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              Mensagens Recentes
            </CardTitle>
            <CardDescription>
              Últimas interações via WhatsApp
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">{msg.from}</Badge>
                      <span className="text-xs text-gray-500">
                        {new Date(msg.timestamp).toLocaleString('pt-BR')}
                      </span>
                    </div>
                    <Badge variant={msg.status === 'received' ? 'default' : 'secondary'}>
                      {msg.status === 'received' ? 'Recebida' : 'Enviada'}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="bg-gray-50 p-3 rounded-lg">
                      <p className="text-sm"><strong>Cliente:</strong> {msg.message}</p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <p className="text-sm"><strong>Agente:</strong> {msg.response}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recursos Avançados */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Automações
            </CardTitle>
            <CardDescription>
              Configure respostas automáticas inteligentes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">Auto-resposta para orçamentos</p>
                  <p className="text-xs text-gray-600">Coleta dados automaticamente</p>
                </div>
                <Badge variant="default">Ativo</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">Detecção de problemas técnicos</p>
                  <p className="text-xs text-gray-600">Identifica palavras-chave</p>
                </div>
                <Badge variant="default">Ativo</Badge>
              </div>
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">Sugestão de produtos</p>
                  <p className="text-xs text-gray-600">Baseado no contexto</p>
                </div>
                <Badge variant="secondary">Inativo</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Analytics
            </CardTitle>
            <CardDescription>
              Métricas de performance do atendimento
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">Conversas hoje</span>
                <span className="font-bold">24</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Orçamentos solicitados</span>
                <span className="font-bold">8</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Problemas resolvidos</span>
                <span className="font-bold">15</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Taxa de conversão</span>
                <span className="font-bold text-green-600">32%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default WhatsAppIntegration
