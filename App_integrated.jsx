import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button.jsx';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx';
import { Input } from '@/components/ui/input.jsx';
import { Textarea } from '@/components/ui/textarea.jsx';
import { Badge } from '@/components/ui/badge.jsx';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx';
import { MessageCircle, Calculator, BookOpen, Palette, Wrench, Lightbulb, Brain, Smartphone, Search, Loader2, Database, Activity, Settings } from 'lucide-react';
import LearningSystem from './components/LearningSystem.jsx';
import WhatsAppIntegration from './components/WhatsAppIntegration.jsx';
import ProductAdmin from './components/ProductAdmin.jsx';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [products, setProducts] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [apiStatus, setApiStatus] = useState('checking');
  const [sessionId] = useState(`web_${Date.now()}`);
  const [systemStats, setSystemStats] = useState({});
  const [whatsappStatus, setWhatsappStatus] = useState('Verificando...');
  const [conversations, setConversations] = useState([]);
  const [systemConfig, setSystemConfig] = useState({});

  // Verificar status da API ao carregar
  useEffect(() => {
    checkApiHealth();
    loadProducts();
    loadSystemStats();
    checkWhatsAppStatus();
    loadConversations();
    loadSystemConfig();
  }, []);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        const data = await response.json();
        setApiStatus('connected');
        setSystemStats(data.services || {});
      } else {
        setApiStatus('error');
      }
    } catch (error) {
      setApiStatus('error');
      console.error('Erro ao conectar com a API:', error);
    }
  };

  const loadSystemStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/stats`);
      if (response.ok) {
        const data = await response.json();
        setSystemStats(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const checkWhatsAppStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/whatsapp/instance/status`);
      if (response.ok) {
        const data = await response.json();
        setWhatsappStatus(data.state || 'Desconectado');
      } else {
        setWhatsappStatus('Não configurado');
      }
    } catch (error) {
      setWhatsappStatus('Erro de conexão');
      console.error('Erro ao verificar status WhatsApp:', error);
    }
  };

  const loadConversations = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/conversations`);
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error('Erro ao carregar conversas:', error);
    }
  };

  const loadSystemConfig = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/config`);
      if (response.ok) {
        const data = await response.json();
        setSystemConfig(data);
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
    }
  };

  const loadProducts = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/products`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || []);
      }
    } catch (error) {
      console.error('Erro ao carregar produtos:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage = { type: 'user', content: currentMessage, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: currentMessage,
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        const agentMessage = {
          type: 'agent',
          content: data.agent_response,
          timestamp: new Date(),
          searchResults: data.search_results || []
        };
        setMessages(prev => [...prev, agentMessage]);
      } else {
        throw new Error('Erro na resposta da API');
      }
    } catch (error) {
      const errorMessage = {
        type: 'agent',
        content: 'Desculpe, ocorreu um erro. Tente novamente.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setCurrentMessage('');
      setIsLoading(false);
    }
  };

  const performSemanticSearch = async () => {
    if (!searchQuery.trim() || isSearching) return;

    setIsSearching(true);
    try {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query: searchQuery,
          top_k: 5,
          similarity_threshold: 0.3
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results || []);
      }
    } catch (error) {
      console.error('Erro na busca semântica:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const generateQuote = async (productId, area) => {
    const areaValue = parseFloat(area);
    if (!areaValue || areaValue <= 0) {
      alert('Por favor, informe uma área válida.');
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/quote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: productId,
          area: areaValue,
          coats: 2,
          labor_included: false,
          session_id: sessionId
        })
      });

      if (response.ok) {
        const data = await response.json();
        const quote = data.quote;
        
        alert(`Orçamento Gerado:\n\nProduto: ${quote.product.name}\nÁrea: ${quote.area}m²\nLitros necessários: ${quote.liters_needed}L\nEmbalagem recomendada: ${quote.recommended_package.quantity}x ${quote.recommended_package.size}L\nCusto total: R$ ${quote.total_cost.toFixed(2)}`);
      } else {
        throw new Error('Erro ao gerar orçamento');
      }
    } catch (error) {
      alert('Erro ao gerar orçamento. Tente novamente.');
      console.error('Erro:', error);
    }
  };

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'connected':
        return '🟢 IA Avançada';
      case 'error':
        return '🔴 Erro de Conexão';
      default:
        return '🟡 Verificando...';
    }
  };

  const getWhatsAppStatusIcon = () => {
    switch (whatsappStatus) {
      case 'open':
        return '🟢 Conectado';
      case 'connecting':
        return '🟡 Conectando...';
      case 'close':
        return '🔴 Desconectado';
      default:
        return '⚪ ' + whatsappStatus;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto p-4">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🎨 Agente Especialista em Tintas
          </h1>
          <p className="text-gray-600 mb-4">
            Seu assistente inteligente para recomendações, cálculos e orçamentos de tintas
          </p>
          <div className="flex justify-center gap-4 text-sm">
            <Badge variant="outline">{getStatusIcon()}</Badge>
            <Badge variant="outline">WhatsApp: {getWhatsAppStatusIcon()}</Badge>
            <Badge variant="outline">
              <Database className="w-3 h-3 mr-1" />
              {systemConfig.services?.supabase ? 'Supabase Conectado' : 'Modo Local'}
            </Badge>
          </div>
        </header>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-8">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <MessageCircle className="w-4 h-4" />
              Chat
            </TabsTrigger>
            <TabsTrigger value="calculator" className="flex items-center gap-2">
              <Calculator className="w-4 h-4" />
              Calculadora
            </TabsTrigger>
            <TabsTrigger value="products" className="flex items-center gap-2">
              <Palette className="w-4 h-4" />
              Produtos
            </TabsTrigger>
            <TabsTrigger value="faq" className="flex items-center gap-2">
              <BookOpen className="w-4 h-4" />
              FAQ
            </TabsTrigger>
            <TabsTrigger value="learning" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Aprendizado
            </TabsTrigger>
            <TabsTrigger value="whatsapp" className="flex items-center gap-2">
              <Smartphone className="w-4 h-4" />
              WhatsApp
            </TabsTrigger>
            <TabsTrigger value="admin" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Admin
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              Analytics
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Chat Principal */}
              <div className="lg:col-span-2">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageCircle className="w-5 h-5" />
                      Chat com Especialista
                    </CardTitle>
                    <CardDescription>
                      Converse com nosso especialista em tintas com 20 anos de experiência
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-96 overflow-y-auto border rounded-lg p-4 mb-4 bg-gray-50">
                      {messages.length === 0 && (
                        <div className="text-center text-gray-500 mt-8">
                          <MessageCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                          <p>Inicie uma conversa! Pergunte sobre tintas, cores, aplicação ou solicite um orçamento.</p>
                        </div>
                      )}
                      {messages.map((message, index) => (
                        <div key={index} className={`mb-4 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                          <div className={`inline-block p-3 rounded-lg max-w-xs lg:max-w-md ${
                            message.type === 'user' 
                              ? 'bg-blue-500 text-white' 
                              : 'bg-white border shadow-sm'
                          }`}>
                            <div className="whitespace-pre-wrap">{message.content}</div>
                            {message.searchResults && message.searchResults.length > 0 && (
                              <div className="mt-2 pt-2 border-t border-gray-200">
                                <div className="text-xs text-gray-500 mb-1">Produtos encontrados:</div>
                                {message.searchResults.slice(0, 2).map((result, idx) => (
                                  <div key={idx} className="text-xs bg-gray-100 p-1 rounded mb-1">
                                    {result.document?.product_name} ({(result.similarity_score * 100).toFixed(0)}%)
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                          <div className="text-xs text-gray-400 mt-1">
                            {message.timestamp.toLocaleTimeString()}
                          </div>
                        </div>
                      ))}
                      {isLoading && (
                        <div className="text-left mb-4">
                          <div className="inline-block p-3 rounded-lg bg-white border shadow-sm">
                            <Loader2 className="w-4 h-4 animate-spin" />
                            <span className="ml-2">Pensando...</span>
                          </div>
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Input
                        value={currentMessage}
                        onChange={(e) => setCurrentMessage(e.target.value)}
                        placeholder="Digite sua pergunta sobre tintas..."
                        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                        disabled={isLoading}
                      />
                      <Button onClick={sendMessage} disabled={isLoading || !currentMessage.trim()}>
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Enviar'}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Busca Semântica */}
              <div>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Search className="w-5 h-5" />
                      Busca Semântica
                    </CardTitle>
                    <CardDescription>
                      Busque produtos por características ou necessidades
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex gap-2 mb-4">
                      <Input
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        placeholder="Ex: tinta lavável para quarto"
                        onKeyPress={(e) => e.key === 'Enter' && performSemanticSearch()}
                      />
                      <Button onClick={performSemanticSearch} disabled={isSearching}>
                        {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                      </Button>
                    </div>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {searchResults.map((result, index) => (
                        <div key={index} className="p-2 border rounded-lg bg-gray-50">
                          <div className="font-medium text-sm">
                            {result.document?.product_name || 'Produto'}
                          </div>
                          <div className="text-xs text-gray-600">
                            {result.document?.brand} - {(result.similarity_score * 100).toFixed(0)}% relevante
                          </div>
                          {result.document?.type && (
                            <div className="text-xs text-blue-600">
                              {result.document.type}
                            </div>
                          )}
                        </div>
                      ))}
                      {searchResults.length === 0 && searchQuery && !isSearching && (
                        <div className="text-center text-gray-500 py-4">
                          Nenhum resultado encontrado
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="calculator" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="w-5 h-5" />
                  Calculadora de Tinta
                </CardTitle>
                <CardDescription>
                  Calcule a quantidade exata de tinta necessária para seu projeto
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PaintCalculator />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="products" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5" />
                  Catálogo de Produtos
                </CardTitle>
                <CardDescription>
                  Explore nosso catálogo completo de tintas e solicite orçamentos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {products.map((product) => (
                    <Card key={product.id} className="border-2 hover:border-blue-300 transition-colors">
                      <CardHeader>
                        <CardTitle className="text-lg">{product.name}</CardTitle>
                        <CardDescription>{product.brand}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2">
                          <p className="text-sm"><strong>Tipo:</strong> {product.type}</p>
                          <p className="text-sm"><strong>Rendimento:</strong> {product.coverage}</p>
                          <p className="text-sm text-gray-600">{product.description}</p>
                          
                          {product.packages && product.packages.length > 0 && (
                            <div className="mt-3">
                              <p className="text-sm font-medium mb-2">Embalagens disponíveis:</p>
                              {product.packages.map((pkg, idx) => (
                                <div key={idx} className="text-xs bg-gray-100 p-2 rounded mb-1">
                                  {pkg.size}L - R$ {pkg.price.toFixed(2)}
                                </div>
                              ))}
                            </div>
                          )}
                          
                          <Button 
                            className="w-full mt-3" 
                            onClick={() => {
                              const area = prompt('Informe a área a ser pintada (em m²):');
                              if (area) generateQuote(product.id, area);
                            }}
                          >
                            Solicitar Orçamento
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                {products.length === 0 && (
                  <div className="text-center text-gray-500 py-8">
                    <Palette className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                    <p>Nenhum produto encontrado. Verifique a conexão com a API.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="faq" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Perguntas Frequentes
                </CardTitle>
                <CardDescription>
                  Respostas para as dúvidas mais comuns sobre tintas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <FAQ />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="learning" className="space-y-4">
            <LearningSystem />
          </TabsContent>

          <TabsContent value="whatsapp" className="space-y-4">
            <WhatsAppIntegration 
              status={whatsappStatus}
              onStatusChange={setWhatsappStatus}
              conversations={conversations}
              onRefreshConversations={loadConversations}
            />
          </TabsContent>

          <TabsContent value="admin" className="space-y-4">
            <ProductAdmin onProductsChange={loadProducts} />
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Analytics e Estatísticas
                </CardTitle>
                <CardDescription>
                  Métricas de uso e performance do sistema
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-2xl font-bold text-blue-600">
                        {systemStats.total_products || 0}
                      </div>
                      <div className="text-sm text-gray-600">Produtos</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-2xl font-bold text-green-600">
                        {systemStats.total_conversations || 0}
                      </div>
                      <div className="text-sm text-gray-600">Conversas</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-2xl font-bold text-purple-600">
                        {systemStats.total_messages || 0}
                      </div>
                      <div className="text-sm text-gray-600">Mensagens</div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="text-2xl font-bold text-orange-600">
                        {systemStats.total_quotes || 0}
                      </div>
                      <div className="text-sm text-gray-600">Orçamentos</div>
                    </CardContent>
                  </Card>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Status dos Serviços</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span>Supabase</span>
                          <Badge variant={systemConfig.services?.supabase ? "default" : "secondary"}>
                            {systemConfig.services?.supabase ? "Conectado" : "Desconectado"}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Evolution API</span>
                          <Badge variant={systemConfig.services?.evolution_api ? "default" : "secondary"}>
                            {systemConfig.services?.evolution_api ? "Configurada" : "Não configurada"}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>Busca Semântica</span>
                          <Badge variant={systemConfig.services?.semantic_search ? "default" : "secondary"}>
                            {systemConfig.services?.semantic_search ? "Ativa" : "Inativa"}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span>WhatsApp</span>
                          <Badge variant={whatsappStatus === 'open' ? "default" : "secondary"}>
                            {getWhatsAppStatusIcon()}
                          </Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle>Conversas Recentes</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {conversations.slice(0, 10).map((conv, index) => (
                          <div key={index} className="flex justify-between items-center p-2 border rounded">
                            <div>
                              <div className="font-medium text-sm">
                                {conv.platform === 'whatsapp' ? '📱 WhatsApp' : '💻 Web'}
                              </div>
                              <div className="text-xs text-gray-600">
                                {conv.phone_number || conv.session_id}
                              </div>
                            </div>
                            <div className="text-xs text-gray-500">
                              {new Date(conv.created_at).toLocaleDateString()}
                            </div>
                          </div>
                        ))}
                        {conversations.length === 0 && (
                          <div className="text-center text-gray-500 py-4">
                            Nenhuma conversa encontrada
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Componente da Calculadora de Tinta
function PaintCalculator() {
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [walls, setWalls] = useState('4');
  const [openings, setOpenings] = useState('');
  const [coverage, setCoverage] = useState('12');
  const [coats, setCoats] = useState('2');
  const [result, setResult] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const calculatePaint = async () => {
    if (!width || !height || !walls) {
      alert('Por favor, preencha largura, altura e número de paredes.');
      return;
    }

    setIsCalculating(true);
    try {
      const response = await fetch(`${API_BASE_URL}/calculate-paint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          width: parseFloat(width),
          height: parseFloat(height),
          walls: parseInt(walls),
          openings: parseFloat(openings) || 0,
          coverage: parseFloat(coverage),
          coats: parseInt(coats)
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResult(data);
      } else {
        throw new Error('Erro no cálculo');
      }
    } catch (error) {
      alert('Erro ao calcular. Verifique os valores informados.');
    } finally {
      setIsCalculating(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Largura (metros)</label>
          <Input
            type="number"
            value={width}
            onChange={(e) => setWidth(e.target.value)}
            placeholder="Ex: 4.5"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Altura (metros)</label>
          <Input
            type="number"
            value={height}
            onChange={(e) => setHeight(e.target.value)}
            placeholder="Ex: 2.8"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Número de Paredes</label>
          <Input
            type="number"
            value={walls}
            onChange={(e) => setWalls(e.target.value)}
            placeholder="Ex: 4"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Área de Vãos (m²)</label>
          <Input
            type="number"
            value={openings}
            onChange={(e) => setOpenings(e.target.value)}
            placeholder="Ex: 2 (portas e janelas)"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Rendimento (m²/L)</label>
          <Input
            type="number"
            value={coverage}
            onChange={(e) => setCoverage(e.target.value)}
            placeholder="Ex: 12"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Número de Demãos</label>
          <Input
            type="number"
            value={coats}
            onChange={(e) => setCoats(e.target.value)}
            placeholder="Ex: 2"
          />
        </div>
      </div>

      <Button onClick={calculatePaint} disabled={isCalculating} className="w-full">
        {isCalculating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Calculator className="w-4 h-4 mr-2" />}
        Calcular Quantidade
      </Button>

      {result && (
        <Card className="bg-green-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-green-800">Resultado do Cálculo</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p><strong>Área total a pintar:</strong> {result.total_area} m²</p>
              <p><strong>Quantidade de tinta:</strong> {result.liters_needed} litros</p>
              <p><strong>Embalagem sugerida:</strong> {result.suggested_package}</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// Componente FAQ
function FAQ() {
  const faqs = [
    {
      question: "Qual a diferença entre tinta acrílica e esmalte?",
      answer: "Tinta acrílica é à base de água, seca mais rápido, tem menos odor e é mais fácil de limpar. Esmalte é à base de solvente, mais resistente e durável, ideal para áreas que precisam de maior proteção."
    },
    {
      question: "Como calcular a quantidade de tinta necessária?",
      answer: "Use a fórmula: Área total (m²) ÷ Rendimento da tinta (m²/L) × Número de demãos + 10% para perdas. Nossa calculadora faz isso automaticamente!"
    },
    {
      question: "Qual tinta usar em área externa?",
      answer: "Para áreas externas, recomendo tintas acrílicas de alta qualidade com proteção UV, como Coral Acrílica Premium ou Suvinil Diamante. Elas resistem melhor às intempéries."
    },
    {
      question: "Como preparar a parede antes de pintar?",
      answer: "1) Limpe a superfície, 2) Remova tintas soltas, 3) Corrija imperfeições com massa, 4) Lixe se necessário, 5) Aplique primer/selador, 6) Aguarde secar completamente."
    },
    {
      question: "Quantas demãos de tinta devo aplicar?",
      answer: "Geralmente 2 demãos são suficientes. Para cores escuras sobre claras ou paredes novas, pode ser necessária uma terceira demão. Sempre respeite o tempo de secagem entre demãos."
    }
  ];

  return (
    <div className="space-y-4">
      {faqs.map((faq, index) => (
        <Card key={index}>
          <CardHeader>
            <CardTitle className="text-lg flex items-start gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-500 mt-0.5" />
              {faq.question}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{faq.answer}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default App;
