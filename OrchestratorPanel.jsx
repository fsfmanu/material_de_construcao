import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  Brain, 
  MessageCircle, 
  Users, 
  Activity,
  ArrowRight,
  CheckCircle,
  Clock,
  AlertCircle,
  BarChart3,
  Settings,
  Zap
} from 'lucide-react';

const OrchestratorPanel = ({ apiUrl = 'http://localhost:5000' }) => {
  const [query, setQuery] = useState('');
  const [orchestrationResult, setOrchestrationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [agentStats, setAgentStats] = useState({});
  const [recentOrchestrations, setRecentOrchestrations] = useState([]);
  const [agentStatus, setAgentStatus] = useState({
    tintas: { status: 'online', load: 'low', response_time: '120ms' },
    pisos: { status: 'online', load: 'medium', response_time: '95ms' },
    orquestrador: { status: 'online', load: 'low', response_time: '50ms' },
    revisor: { status: 'online', load: 'low', response_time: '80ms' }
  });

  useEffect(() => {
    // Simular dados de estatísticas
    setAgentStats({
      total_queries: 1247,
      successful_orchestrations: 1198,
      average_response_time: '98ms',
      agent_distribution: {
        tintas: 45,
        pisos: 35,
        geral: 20
      }
    });

    // Simular orquestrações recentes
    setRecentOrchestrations([
      {
        id: 1,
        query: "Preciso de tinta para parede externa",
        selected_agent: "tintas",
        confidence: 0.95,
        timestamp: "14:32",
        status: "completed"
      },
      {
        id: 2,
        query: "Qual piso é melhor para cozinha?",
        selected_agent: "pisos",
        confidence: 0.88,
        timestamp: "14:28",
        status: "completed"
      },
      {
        id: 3,
        query: "Orçamento para reforma completa",
        selected_agent: "multiple",
        confidence: 0.72,
        timestamp: "14:25",
        status: "in_progress"
      }
    ]);
  }, []);

  const orchestrateQuery = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setOrchestrationResult(null);

    try {
      const response = await fetch(`${apiUrl}/api/orchestrator/route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          context: {
            user_preferences: {},
            conversation_history: []
          }
        }),
      });

      const data = await response.json();

      if (data.routing_decision) {
        setOrchestrationResult({
          query: query,
          routing_decision: data.routing_decision,
          confidence: data.confidence,
          reasoning: data.reasoning,
          suggested_agents: data.suggested_agents,
          response: data.response,
          timestamp: new Date().toLocaleTimeString()
        });

        // Adicionar à lista de orquestrações recentes
        const newOrchestration = {
          id: Date.now(),
          query: query,
          selected_agent: data.routing_decision.primary_agent,
          confidence: data.confidence,
          timestamp: new Date().toLocaleTimeString(),
          status: "completed"
        };

        setRecentOrchestrations(prev => [newOrchestration, ...prev.slice(0, 9)]);
      }
    } catch (error) {
      console.error('Erro na orquestração:', error);
      setOrchestrationResult({
        query: query,
        error: 'Erro ao processar consulta',
        timestamp: new Date().toLocaleTimeString()
      });
    }

    setIsLoading(false);
  };

  const getAgentIcon = (agent) => {
    switch (agent) {
      case 'tintas': return '🎨';
      case 'pisos': return '🏠';
      case 'orquestrador': return '🎭';
      case 'revisor': return '✅';
      case 'multiple': return '👥';
      default: return '🤖';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'busy': return 'bg-yellow-500';
      case 'offline': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getLoadColor = (load) => {
    switch (load) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🎭 Orquestrador de Agentes
        </h2>
        <p className="text-gray-600">
          Coordena e direciona consultas para os agentes especialistas apropriados
        </p>
      </div>

      <Tabs defaultValue="orchestrate" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="orchestrate" className="flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Orquestrar
          </TabsTrigger>
          <TabsTrigger value="agents" className="flex items-center gap-2">
            <Users className="w-4 h-4" />
            Status Agentes
          </TabsTrigger>
          <TabsTrigger value="activity" className="flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Atividade
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="orchestrate" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="w-5 h-5" />
                Orquestração Inteligente
              </CardTitle>
              <CardDescription>
                Digite sua consulta e veja como o orquestrador decide qual agente deve responder
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ex: Preciso de tinta para parede externa e piso para cozinha"
                    onKeyPress={(e) => e.key === 'Enter' && orchestrateQuery()}
                    disabled={isLoading}
                  />
                  <Button onClick={orchestrateQuery} disabled={isLoading || !query.trim()}>
                    {isLoading ? (
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Zap className="w-4 h-4 mr-2" />
                    )}
                    Orquestrar
                  </Button>
                </div>

                {orchestrationResult && (
                  <div className="space-y-4">
                    <div className="border rounded-lg p-4 bg-blue-50">
                      <h3 className="font-semibold mb-3 flex items-center gap-2">
                        <MessageCircle className="w-4 h-4" />
                        Resultado da Orquestração
                      </h3>
                      
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm font-medium text-gray-700">Consulta:</p>
                          <p className="text-sm bg-white p-2 rounded border">{orchestrationResult.query}</p>
                        </div>

                        {orchestrationResult.error ? (
                          <div className="flex items-center gap-2 text-red-600">
                            <AlertCircle className="w-4 h-4" />
                            <span className="text-sm">{orchestrationResult.error}</span>
                          </div>
                        ) : (
                          <>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <p className="text-sm font-medium text-gray-700 mb-2">Agente Selecionado:</p>
                                <div className="flex items-center gap-2">
                                  <span className="text-2xl">{getAgentIcon(orchestrationResult.routing_decision.primary_agent)}</span>
                                  <Badge variant="default" className="capitalize">
                                    {orchestrationResult.routing_decision.primary_agent}
                                  </Badge>
                                  <Badge variant="outline">
                                    {Math.round(orchestrationResult.confidence * 100)}% confiança
                                  </Badge>
                                </div>
                              </div>

                              <div>
                                <p className="text-sm font-medium text-gray-700 mb-2">Estratégia:</p>
                                <Badge variant="secondary" className="capitalize">
                                  {orchestrationResult.routing_decision.strategy}
                                </Badge>
                              </div>
                            </div>

                            {orchestrationResult.reasoning && (
                              <div>
                                <p className="text-sm font-medium text-gray-700">Raciocínio:</p>
                                <p className="text-sm bg-white p-2 rounded border">{orchestrationResult.reasoning}</p>
                              </div>
                            )}

                            {orchestrationResult.suggested_agents && orchestrationResult.suggested_agents.length > 1 && (
                              <div>
                                <p className="text-sm font-medium text-gray-700 mb-2">Agentes Sugeridos:</p>
                                <div className="flex flex-wrap gap-2">
                                  {orchestrationResult.suggested_agents.map((agent, idx) => (
                                    <div key={idx} className="flex items-center gap-1">
                                      <span>{getAgentIcon(agent.agent)}</span>
                                      <Badge variant="outline" className="capitalize">
                                        {agent.agent} ({Math.round(agent.confidence * 100)}%)
                                      </Badge>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {orchestrationResult.response && (
                              <div>
                                <p className="text-sm font-medium text-gray-700">Resposta do Agente:</p>
                                <div className="bg-white p-3 rounded border">
                                  <p className="text-sm">{orchestrationResult.response}</p>
                                </div>
                              </div>
                            )}
                          </>
                        )}

                        <div className="text-xs text-gray-500 flex items-center gap-2">
                          <Clock className="w-3 h-3" />
                          Processado às {orchestrationResult.timestamp}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agents" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(agentStatus).map(([agent, status]) => (
              <Card key={agent}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg capitalize flex items-center gap-2">
                      <span className="text-2xl">{getAgentIcon(agent)}</span>
                      {agent}
                    </CardTitle>
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(status.status)}`}></div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Status:</span>
                    <Badge variant={status.status === 'online' ? 'default' : 'secondary'}>
                      {status.status}
                    </Badge>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Carga:</span>
                    <span className={`text-sm font-medium ${getLoadColor(status.load)}`}>
                      {status.load}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Resposta:</span>
                    <span className="text-sm font-medium">{status.response_time}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Atividade Recente
              </CardTitle>
              <CardDescription>
                Últimas orquestrações realizadas pelo sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentOrchestrations.map((orchestration) => (
                  <div key={orchestration.id} className="border rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getAgentIcon(orchestration.selected_agent)}</span>
                        <span className="font-medium capitalize">{orchestration.selected_agent}</span>
                        <Badge variant="outline">
                          {Math.round(orchestration.confidence * 100)}%
                        </Badge>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        {orchestration.status === 'completed' ? (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        ) : (
                          <Clock className="w-4 h-4 text-yellow-500 animate-spin" />
                        )}
                        <span className="text-sm text-gray-500">{orchestration.timestamp}</span>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-700">{orchestration.query}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Total de Consultas</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {agentStats.total_queries?.toLocaleString()}
                </div>
                <p className="text-sm text-gray-600">Consultas processadas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Taxa de Sucesso</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {agentStats.successful_orchestrations && agentStats.total_queries ? 
                    Math.round((agentStats.successful_orchestrations / agentStats.total_queries) * 100) : 0}%
                </div>
                <p className="text-sm text-gray-600">Orquestrações bem-sucedidas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Tempo Médio</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">
                  {agentStats.average_response_time}
                </div>
                <p className="text-sm text-gray-600">Tempo de resposta</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Agente Mais Usado</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  🎨 Tintas
                </div>
                <p className="text-sm text-gray-600">
                  {agentStats.agent_distribution?.tintas}% das consultas
                </p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Distribuição por Agente</CardTitle>
              <CardDescription>
                Porcentagem de consultas direcionadas para cada agente
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {agentStats.agent_distribution && Object.entries(agentStats.agent_distribution).map(([agent, percentage]) => (
                  <div key={agent} className="flex items-center gap-3">
                    <span className="text-lg">{getAgentIcon(agent)}</span>
                    <span className="capitalize font-medium w-20">{agent}</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium w-12">{percentage}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default OrchestratorPanel;
