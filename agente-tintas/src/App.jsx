import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { MessageCircle, Calculator, BookOpen, Palette, Wrench, Lightbulb, Brain, Smartphone } from 'lucide-react'
import LearningSystem from './components/LearningSystem.jsx'
import WhatsAppIntegration from './components/WhatsAppIntegration.jsx'
import './App.css'

function App() {
  const [messages, setMessages] = useState([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  // Base de conhecimento simplificada para demonstração
  const knowledgeBase = {
    brands: [
      { name: 'Coral Master', type: 'Acrílica Premium', coverage: '14-16 m²/L', features: ['Alta cobertura', 'Secagem rápida', 'Fácil aplicação'] },
      { name: 'Coral Super Lavável', type: 'Antimanchas', coverage: '12-14 m²/L', features: ['Repele líquidos', '99% antibactéria', 'Lavável'] },
      { name: 'Elit Super', type: 'Custo-benefício', coverage: '10-12 m²/L', features: ['Secagem rápida', 'Resistente', 'Profissional'] },
      { name: 'Sherwin-Williams ProClassic', type: 'Premium Internacional', coverage: '12-14 m²/L', features: ['Não amarela', 'Alta durabilidade', 'Acabamento luxuoso'] }
    ],
    faq: [
      {
        question: 'Qual a diferença entre tinta acrílica premium e econômica?',
        answer: 'Tintas acrílicas premium oferecem maior rendimento (14-16 m²/L), cobertura superior, durabilidade estendida e tecnologias adicionais como antimofo/antibactéria. As econômicas têm menor rendimento (8-10 m²/L) e durabilidade, adequadas para projetos com orçamento limitado.'
      },
      {
        question: 'Como calcular a quantidade de tinta necessária?',
        answer: 'Use a fórmula: Litros = (Largura × Altura × Número de Paredes - Vãos) ÷ Rendimento por Litro ÷ Número de Demãos. Adicione 10% para perdas e retoques.'
      },
      {
        question: 'Minha parede está descascando. O que fazer?',
        answer: 'Descascamento indica má preparação ou umidade. Remova todas as camadas soltas, trate a causa da umidade e aplique primer adequado antes de repintar com sistema completo.'
      },
      {
        question: 'Posso pintar madeira com tinta acrílica?',
        answer: 'Para madeira externa, recomenda-se sistema premium com proteção (Stain ou selador) e acabamento com verniz ou esmalte específico. Tintas acrílicas residenciais podem não oferecer proteção adequada.'
      }
    ]
  }

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return

    const userMessage = { type: 'user', content: currentMessage }
    setMessages(prev => [...prev, userMessage])
    setCurrentMessage('')
    setIsLoading(true)

    // Simular resposta do agente baseada na base de conhecimento
    setTimeout(() => {
      let response = 'Olá! Sou seu especialista em tintas com 20 anos de experiência. '
      
      // Análise simples da mensagem para dar resposta contextual
      const message = currentMessage.toLowerCase()
      
      if (message.includes('orçamento') || message.includes('preço') || message.includes('custo')) {
        response += 'Para elaborar um orçamento preciso, preciso saber: 1) Tipo de projeto (residencial/automotivo), 2) Superfície a pintar, 3) Área em m², 4) Condições do ambiente. Você pode me fornecer essas informações?'
      } else if (message.includes('coral') || message.includes('master')) {
        response += 'A Coral Master é uma excelente escolha! É uma tinta acrílica premium com alta consistência, rendimento de 14-16 m²/L, secagem rápida (30min ao toque) e excelente cobertura. Ideal para quem busca qualidade profissional.'
      } else if (message.includes('descasca') || message.includes('problema')) {
        response += 'Problemas de descascamento geralmente indicam: 1) Superfície mal preparada (80% dos casos), 2) Umidade, 3) Incompatibilidade química. Recomendo remoção completa das camadas soltas, tratamento da umidade na fonte e aplicação de primer adequado.'
      } else if (message.includes('calcul') || message.includes('quantidade')) {
        response += 'Para calcular a tinta necessária: Área Total = (Largura × Altura × Paredes) - Vãos. Litros = Área ÷ Rendimento ÷ Demãos + 10% para perdas. Qual a área que você precisa pintar?'
      } else {
        response += 'Como posso ajudá-lo hoje? Posso auxiliar com: recomendações de produtos, cálculo de materiais, solução de problemas, orçamentos, escolha de cores e sistemas de pintura. Qual sua necessidade específica?'
      }

      const botMessage = { type: 'bot', content: response }
      setMessages(prev => [...prev, botMessage])
      setIsLoading(false)
    }, 1500)
  }

  const calculatePaint = (area, coverage = 12, coats = 2) => {
    const liters = (area / coverage / coats) * 1.1 // 10% extra
    return Math.ceil(liters * 10) / 10 // Round up to 1 decimal
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-orange-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Palette className="h-10 w-10 text-orange-600" />
            <h1 className="text-4xl font-bold text-gray-800">Agente Especialista em Tintas</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Consultoria técnica especializada com 20 anos de experiência. 
            Recomendações, orçamentos e soluções para todos os seus projetos de pintura.
          </p>
        </div>

        <Tabs defaultValue="chat" className="w-full">
          <TabsList className="grid w-full grid-cols-6 mb-8">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Chat Especialista
            </TabsTrigger>
            <TabsTrigger value="calculator" className="flex items-center gap-2">
              <Calculator className="h-4 w-4" />
              Calculadora
            </TabsTrigger>
            <TabsTrigger value="products" className="flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              Produtos
            </TabsTrigger>
            <TabsTrigger value="faq" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              FAQ
            </TabsTrigger>
            <TabsTrigger value="learning" className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Aprendizado
            </TabsTrigger>
            <TabsTrigger value="whatsapp" className="flex items-center gap-2">
              <Smartphone className="h-4 w-4" />
              WhatsApp
            </TabsTrigger>
          </TabsList>

          {/* Chat Tab */}
          <TabsContent value="chat">
            <Card className="h-[600px] flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageCircle className="h-5 w-5" />
                  Consultor Técnico Virtual
                </CardTitle>
                <CardDescription>
                  Tire suas dúvidas sobre tintas, obtenha recomendações técnicas e solicite orçamentos
                </CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                <div className="flex-1 overflow-y-auto mb-4 space-y-4 p-4 bg-gray-50 rounded-lg">
                  {messages.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                      <Lightbulb className="h-12 w-12 mx-auto mb-4 text-orange-400" />
                      <p>Olá! Sou seu especialista em tintas. Como posso ajudá-lo hoje?</p>
                      <p className="text-sm mt-2">Pergunte sobre produtos, peça orçamentos ou tire dúvidas técnicas!</p>
                    </div>
                  )}
                  {messages.map((msg, index) => (
                    <div key={index} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-[80%] p-3 rounded-lg ${
                        msg.type === 'user' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white text-gray-800 shadow-sm border'
                      }`}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-white p-3 rounded-lg shadow-sm border">
                        <div className="flex items-center gap-2">
                          <div className="animate-spin h-4 w-4 border-2 border-orange-600 border-t-transparent rounded-full"></div>
                          Analisando sua consulta...
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                    placeholder="Digite sua pergunta sobre tintas..."
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className="flex-1"
                  />
                  <Button onClick={handleSendMessage} disabled={isLoading}>
                    Enviar
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Calculator Tab */}
          <TabsContent value="calculator">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Calculator className="h-5 w-5" />
                    Calculadora de Tinta
                  </CardTitle>
                  <CardDescription>
                    Calcule a quantidade de tinta necessária para seu projeto
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Largura (metros)</label>
                    <Input type="number" placeholder="Ex: 4.5" id="width" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Altura (metros)</label>
                    <Input type="number" placeholder="Ex: 2.8" id="height" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Número de Paredes</label>
                    <Input type="number" placeholder="Ex: 4" id="walls" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Área de Vãos (m²)</label>
                    <Input type="number" placeholder="Ex: 3.5" id="openings" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Rendimento da Tinta (m²/L)</label>
                    <Input type="number" placeholder="Ex: 12" id="coverage" defaultValue="12" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Número de Demãos</label>
                    <Input type="number" placeholder="Ex: 2" id="coats" defaultValue="2" />
                  </div>
                  <Button 
                    className="w-full" 
                    onClick={() => {
                      const width = parseFloat(document.getElementById('width').value) || 0
                      const height = parseFloat(document.getElementById('height').value) || 0
                      const walls = parseFloat(document.getElementById('walls').value) || 0
                      const openings = parseFloat(document.getElementById('openings').value) || 0
                      const coverage = parseFloat(document.getElementById('coverage').value) || 12
                      const coats = parseFloat(document.getElementById('coats').value) || 2
                      
                      const totalArea = (width * height * walls) - openings
                      const liters = calculatePaint(totalArea, coverage, coats)
                      
                      alert(`Área total: ${totalArea.toFixed(1)} m²\nQuantidade necessária: ${liters} litros\n(Já inclusos 10% para perdas e retoques)`)
                    }}
                  >
                    Calcular Quantidade
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Dicas de Cálculo</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-800 mb-2">Rendimento por Categoria</h4>
                    <ul className="text-sm text-blue-700 space-y-1">
                      <li>• Premium: 14-16 m²/L</li>
                      <li>• Standard: 10-12 m²/L</li>
                      <li>• Econômica: 8-10 m²/L</li>
                    </ul>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-semibold text-orange-800 mb-2">Lembre-se</h4>
                    <ul className="text-sm text-orange-700 space-y-1">
                      <li>• Sempre adicione 10% para perdas</li>
                      <li>• Considere o número de demãos</li>
                      <li>• Desconte vãos (portas/janelas)</li>
                      <li>• Superfícies porosas consomem mais</li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Products Tab */}
          <TabsContent value="products">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {knowledgeBase.brands.map((product, index) => (
                <Card key={index} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="text-lg">{product.name}</CardTitle>
                    <CardDescription>{product.type}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Rendimento:</span>
                        <Badge variant="secondary">{product.coverage}</Badge>
                      </div>
                      <div>
                        <span className="text-sm font-medium mb-2 block">Características:</span>
                        <div className="flex flex-wrap gap-1">
                          {product.features.map((feature, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      <Button variant="outline" className="w-full">
                        Solicitar Orçamento
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Precisa de um produto específico?</CardTitle>
                <CardDescription>
                  Nosso catálogo completo será carregado assim que você fornecer sua lista de produtos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <p className="text-yellow-800">
                    🔄 <strong>Aguardando lista de produtos:</strong> Para ativar a funcionalidade completa de orçamentos, 
                    forneça a lista dos produtos que você comercializa com seus respectivos preços.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* FAQ Tab */}
          <TabsContent value="faq">
            <div className="space-y-4">
              {knowledgeBase.faq.map((item, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="text-lg">{item.question}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-700">{item.answer}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Não encontrou sua dúvida?</CardTitle>
                <CardDescription>
                  Use o chat especialista para fazer perguntas específicas sobre seu projeto
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => document.querySelector('[value="chat"]').click()}>
                  Ir para o Chat Especialista
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Learning System Tab */}
          <TabsContent value="learning">
            <LearningSystem />
          </TabsContent>

          {/* WhatsApp Integration Tab */}
          <TabsContent value="whatsapp">
            <WhatsAppIntegration />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default App
