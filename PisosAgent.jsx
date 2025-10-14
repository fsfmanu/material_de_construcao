import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  MessageCircle, 
  Calculator, 
  Package, 
  Search,
  Ruler,
  Palette,
  Home,
  Droplets,
  Shield,
  Zap
} from 'lucide-react';

const PisosAgent = ({ apiUrl = 'http://localhost:5000' }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [calculatorData, setCalculatorData] = useState({
    comprimento: '',
    largura: '',
    area_desperdicada: '10',
    tipo_piso: 'ceramico'
  });
  const [calculatorResult, setCalculatorResult] = useState(null);
  const [products, setProducts] = useState([]);

  // Produtos de exemplo para pisos
  const exampleProducts = [
    {
      id: 1,
      name: "Porcelanato Acetinado Carrara",
      brand: "Portinari",
      type: "Porcelanato",
      size: "60x60cm",
      price: 89.90,
      coverage: "0.36m²/peça",
      features: ["Acetinado", "Antiderrapante", "Resistente"],
      use_case: ["Sala", "Cozinha", "Área Externa"],
      description: "Porcelanato acetinado com visual de mármore Carrara, ideal para ambientes sofisticados."
    },
    {
      id: 2,
      name: "Cerâmica Esmaltada Madeira",
      brand: "Eliane",
      type: "Cerâmica",
      size: "20x120cm",
      price: 45.50,
      coverage: "0.24m²/peça",
      features: ["Esmaltada", "Efeito Madeira", "Fácil Limpeza"],
      use_case: ["Quarto", "Sala", "Escritório"],
      description: "Cerâmica com efeito madeira, perfeita para criar ambientes aconchegantes."
    },
    {
      id: 3,
      name: "Piso Laminado Carvalho",
      brand: "Durafloor",
      type: "Laminado",
      size: "19x138cm",
      price: 32.90,
      coverage: "0.262m²/peça",
      features: ["Resistente à Água", "Fácil Instalação", "Conforto Térmico"],
      use_case: ["Quarto", "Sala", "Escritório"],
      description: "Piso laminado com visual de carvalho natural, resistente e durável."
    },
    {
      id: 4,
      name: "Piso Vinílico SPC Stone",
      brand: "Tarkett",
      type: "Vinílico",
      size: "18x122cm",
      price: 67.80,
      coverage: "0.22m²/peça",
      features: ["100% Impermeável", "Antibacteriano", "Conforto Acústico"],
      use_case: ["Banheiro", "Cozinha", "Área de Serviço"],
      description: "Piso vinílico SPC com visual de pedra, totalmente impermeável."
    }
  ];

  useEffect(() => {
    setProducts(exampleProducts);
    // Mensagem inicial do agente de pisos
    setMessages([{
      type: 'agent',
      content: 'Olá! Sou o especialista em pisos e revestimentos. Posso ajudá-lo com dúvidas sobre tipos de piso, cálculos de quantidade, especificações técnicas e recomendações para cada ambiente. Como posso ajudá-lo hoje?',
      timestamp: new Date().toLocaleTimeString()
    }]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${apiUrl}/api/pisos/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          conversation_history: messages
        }),
      });

      const data = await response.json();

      if (data.response) {
        const agentMessage = {
          type: 'agent',
          content: data.response,
          timestamp: new Date().toLocaleTimeString(),
          products: data.products || [],
          confidence: data.confidence
        };

        setMessages(prev => [...prev, agentMessage]);

        // Atualizar resultados de busca se houver produtos
        if (data.products && data.products.length > 0) {
          setSearchResults(data.products);
        }
      }
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error);
      const errorMessage = {
        type: 'agent',
        content: 'Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente.',
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setInputMessage('');
    setIsLoading(false);
  };

  const calculateQuantity = () => {
    const comprimento = parseFloat(calculatorData.comprimento);
    const largura = parseFloat(calculatorData.largura);
    const desperdicioPercent = parseFloat(calculatorData.area_desperdicada);

    if (!comprimento || !largura) {
      alert('Por favor, preencha o comprimento e largura');
      return;
    }

    const areaTotal = comprimento * largura;
    const areaComDesperdicio = areaTotal * (1 + desperdicioPercent / 100);

    // Cálculos específicos por tipo de piso
    let result = {
      area_total: areaTotal,
      area_com_desperdicio: areaComDesperdicio,
      tipo_piso: calculatorData.tipo_piso
    };

    switch (calculatorData.tipo_piso) {
      case 'ceramico':
        // Exemplo: cerâmica 45x45cm = 0.2025m² por peça
        const areaPorPecaCeramica = 0.2025;
        result.pecas_necessarias = Math.ceil(areaComDesperdicio / areaPorPecaCeramica);
        result.caixas_necessarias = Math.ceil(result.pecas_necessarias / 10); // 10 peças por caixa
        result.area_por_peca = areaPorPecaCeramica;
        result.pecas_por_caixa = 10;
        break;

      case 'porcelanato':
        // Exemplo: porcelanato 60x60cm = 0.36m² por peça
        const areaPorPecaPorcelanato = 0.36;
        result.pecas_necessarias = Math.ceil(areaComDesperdicio / areaPorPecaPorcelanato);
        result.caixas_necessarias = Math.ceil(result.pecas_necessarias / 8); // 8 peças por caixa
        result.area_por_peca = areaPorPecaPorcelanato;
        result.pecas_por_caixa = 8;
        break;

      case 'laminado':
        // Exemplo: laminado vendido por m²
        result.metros_quadrados = Math.ceil(areaComDesperdicio);
        result.caixas_necessarias = Math.ceil(areaComDesperdicio / 2.5); // 2.5m² por caixa
        result.area_por_caixa = 2.5;
        break;

      case 'vinilico':
        // Exemplo: vinílico vendido por m²
        result.metros_quadrados = Math.ceil(areaComDesperdicio);
        result.caixas_necessarias = Math.ceil(areaComDesperdicio / 3.0); // 3.0m² por caixa
        result.area_por_caixa = 3.0;
        break;

      default:
        result.metros_quadrados = Math.ceil(areaComDesperdicio);
    }

    setCalculatorResult(result);
  };

  const requestQuote = (product) => {
    const area = prompt('Digite a área a ser revestida (em m²):');
    if (area && !isNaN(area)) {
      const areaNum = parseFloat(area);
      const coverage = parseFloat(product.coverage.replace('m²/peça', ''));
      const piecesNeeded = Math.ceil(areaNum / coverage);
      const totalPrice = piecesNeeded * product.price;

      alert(`Orçamento para ${product.name}:\n\nÁrea: ${areaNum}m²\nPeças necessárias: ${piecesNeeded}\nPreço unitário: R$ ${product.price.toFixed(2)}\nTotal: R$ ${totalPrice.toFixed(2)}`);
    }
  };

  const getTypeIcon = (type) => {
    switch (type.toLowerCase()) {
      case 'porcelanato': return <Shield className="w-4 h-4" />;
      case 'ceramica': case 'cerâmica': return <Home className="w-4 h-4" />;
      case 'laminado': return <Palette className="w-4 h-4" />;
      case 'vinilico': case 'vinílico': return <Droplets className="w-4 h-4" />;
      default: return <Package className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🏠 Agente Especialista em Pisos e Revestimentos
        </h2>
        <p className="text-gray-600">
          Especialista em pisos cerâmicos, porcelanatos, laminados, vinílicos e revestimentos
        </p>
      </div>

      <Tabs defaultValue="chat" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageCircle className="w-4 h-4" />
            Chat Especialista
          </TabsTrigger>
          <TabsTrigger value="calculator" className="flex items-center gap-2">
            <Calculator className="w-4 h-4" />
            Calculadora
          </TabsTrigger>
          <TabsTrigger value="products" className="flex items-center gap-2">
            <Package className="w-4 h-4" />
            Produtos
          </TabsTrigger>
          <TabsTrigger value="search" className="flex items-center gap-2">
            <Search className="w-4 h-4" />
            Busca
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageCircle className="w-5 h-5" />
                Chat com Especialista em Pisos
              </CardTitle>
              <CardDescription>
                Faça perguntas sobre tipos de piso, especificações técnicas, aplicações e cálculos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="h-96 overflow-y-auto border rounded-lg p-4 space-y-3">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p className="text-xs opacity-70 mt-1">{message.timestamp}</p>
                        {message.products && message.products.length > 0 && (
                          <div className="mt-2 space-y-1">
                            <p className="text-xs font-semibold">Produtos relacionados:</p>
                            {message.products.slice(0, 3).map((product, idx) => (
                              <div key={idx} className="text-xs bg-white bg-opacity-20 rounded p-1">
                                {product.name} - {product.type}
                              </div>
                            ))}
                          </div>
                        )}
                        {message.confidence && (
                          <div className="mt-1">
                            <Badge variant="secondary" className="text-xs">
                              Confiança: {Math.round(message.confidence * 100)}%
                            </Badge>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-gray-100 text-gray-900 max-w-xs lg:max-w-md px-4 py-2 rounded-lg">
                        <p className="text-sm">Especialista está pensando...</p>
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Digite sua pergunta sobre pisos..."
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    disabled={isLoading}
                  />
                  <Button onClick={sendMessage} disabled={isLoading || !inputMessage.trim()}>
                    Enviar
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="calculator" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Calculadora de Pisos
              </CardTitle>
              <CardDescription>
                Calcule a quantidade necessária de pisos para seu projeto
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">
                      <Ruler className="w-4 h-4 inline mr-1" />
                      Comprimento (metros)
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      value={calculatorData.comprimento}
                      onChange={(e) => setCalculatorData({...calculatorData, comprimento: e.target.value})}
                      placeholder="Ex: 5.5"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      <Ruler className="w-4 h-4 inline mr-1" />
                      Largura (metros)
                    </label>
                    <Input
                      type="number"
                      step="0.1"
                      value={calculatorData.largura}
                      onChange={(e) => setCalculatorData({...calculatorData, largura: e.target.value})}
                      placeholder="Ex: 4.2"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Desperdício (%)
                    </label>
                    <Input
                      type="number"
                      value={calculatorData.area_desperdicada}
                      onChange={(e) => setCalculatorData({...calculatorData, area_desperdicada: e.target.value})}
                      placeholder="10"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-1">
                      Tipo de Piso
                    </label>
                    <select
                      className="w-full p-2 border rounded-md"
                      value={calculatorData.tipo_piso}
                      onChange={(e) => setCalculatorData({...calculatorData, tipo_piso: e.target.value})}
                    >
                      <option value="ceramico">Cerâmico</option>
                      <option value="porcelanato">Porcelanato</option>
                      <option value="laminado">Laminado</option>
                      <option value="vinilico">Vinílico</option>
                    </select>
                  </div>

                  <Button onClick={calculateQuantity} className="w-full">
                    <Calculator className="w-4 h-4 mr-2" />
                    Calcular Quantidade
                  </Button>
                </div>

                {calculatorResult && (
                  <div className="space-y-4">
                    <h3 className="font-semibold text-lg">Resultado do Cálculo</h3>
                    
                    <div className="bg-blue-50 p-4 rounded-lg space-y-2">
                      <p><strong>Área total:</strong> {calculatorResult.area_total.toFixed(2)}m²</p>
                      <p><strong>Área com desperdício:</strong> {calculatorResult.area_com_desperdicio.toFixed(2)}m²</p>
                      <p><strong>Tipo de piso:</strong> {calculatorResult.tipo_piso}</p>
                      
                      {calculatorResult.pecas_necessarias && (
                        <>
                          <p><strong>Peças necessárias:</strong> {calculatorResult.pecas_necessarias}</p>
                          <p><strong>Caixas necessárias:</strong> {calculatorResult.caixas_necessarias}</p>
                          <p><strong>Área por peça:</strong> {calculatorResult.area_por_peca}m²</p>
                          <p><strong>Peças por caixa:</strong> {calculatorResult.pecas_por_caixa}</p>
                        </>
                      )}
                      
                      {calculatorResult.metros_quadrados && (
                        <>
                          <p><strong>Metros quadrados:</strong> {calculatorResult.metros_quadrados}m²</p>
                          <p><strong>Caixas necessárias:</strong> {calculatorResult.caixas_necessarias}</p>
                          {calculatorResult.area_por_caixa && (
                            <p><strong>Área por caixa:</strong> {calculatorResult.area_por_caixa}m²</p>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="products" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="w-5 h-5" />
                Catálogo de Pisos
              </CardTitle>
              <CardDescription>
                Explore nossa seleção de pisos e revestimentos
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {products.map((product) => (
                  <Card key={product.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-lg">{product.name}</CardTitle>
                        {getTypeIcon(product.type)}
                      </div>
                      <CardDescription>{product.brand} • {product.size}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Badge variant="outline">{product.type}</Badge>
                        <span className="font-bold text-lg text-green-600">
                          R$ {product.price.toFixed(2)}
                        </span>
                      </div>
                      
                      <p className="text-sm text-gray-600">{product.description}</p>
                      
                      <div>
                        <p className="text-sm font-medium mb-1">Cobertura:</p>
                        <Badge variant="secondary">{product.coverage}</Badge>
                      </div>
                      
                      <div>
                        <p className="text-sm font-medium mb-1">Características:</p>
                        <div className="flex flex-wrap gap-1">
                          {product.features.map((feature, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-sm font-medium mb-1">Indicado para:</p>
                        <div className="flex flex-wrap gap-1">
                          {product.use_case.map((use, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {use}
                            </Badge>
                          ))}
                        </div>
                      </div>
                      
                      <Button 
                        onClick={() => requestQuote(product)} 
                        className="w-full"
                        variant="outline"
                      >
                        Solicitar Orçamento
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="search" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5" />
                Busca Semântica de Pisos
              </CardTitle>
              <CardDescription>
                Encontre pisos usando descrições naturais
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Ex: piso resistente para área externa"
                    className="flex-1"
                  />
                  <Button>
                    <Search className="w-4 h-4 mr-2" />
                    Buscar
                  </Button>
                </div>

                {searchResults.length > 0 && (
                  <div className="space-y-3">
                    <h3 className="font-semibold">Resultados da Busca:</h3>
                    {searchResults.map((result, index) => (
                      <div key={index} className="border rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium">{result.name}</h4>
                          <Badge variant="outline">
                            {Math.round(result.score * 100)}% relevante
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600">{result.description}</p>
                        <div className="flex gap-2 mt-2">
                          <Badge variant="secondary">{result.type}</Badge>
                          <Badge variant="outline">{result.brand}</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PisosAgent;
