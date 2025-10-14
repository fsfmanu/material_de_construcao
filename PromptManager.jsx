import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Trash2, Edit, Plus, Save, RefreshCw, MessageSquare, Bot, Settings } from 'lucide-react';

const PromptManager = () => {
  const [prompts, setPrompts] = useState({});
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('tintas');
  const [editingPrompt, setEditingPrompt] = useState(null);
  const [newPrompt, setNewPrompt] = useState({ agent_type: 'tintas', prompt_type: '', prompt_text: '', description: '' });
  const [showNewPromptDialog, setShowNewPromptDialog] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: '', type: 'info' });

  const agentTypes = [
    { value: 'tintas', label: 'Agente de Tintas', icon: '🎨' },
    { value: 'pisos', label: 'Agente de Pisos', icon: '🏗️' },
    { value: 'orquestrador', label: 'Orquestrador', icon: '🎭' },
    { value: 'revisor', label: 'Revisor', icon: '✅' }
  ];

  const promptTypes = {
    tintas: [
      'initial_greeting',
      'product_recommendation_intro',
      'budget_request',
      'paint_problem_diagnosis',
      'calculation_help',
      'no_results_found',
      'error_message'
    ],
    pisos: [
      'initial_greeting',
      'product_recommendation_intro',
      'installation_advice',
      'maintenance_tips',
      'no_results_found',
      'error_message'
    ],
    orquestrador: [
      'initial_greeting',
      'routing_message',
      'agent_selection',
      'error_message'
    ],
    revisor: [
      'quality_check_intro',
      'revision_complete',
      'improvement_suggestions'
    ]
  };

  useEffect(() => {
    loadPrompts();
  }, []);

  const showAlert = (message, type = 'info') => {
    setAlert({ show: true, message, type });
    setTimeout(() => setAlert({ show: false, message: '', type: 'info' }), 5000);
  };

  const loadPrompts = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/prompts');
      if (response.ok) {
        const data = await response.json();
        setPrompts(data);
        showAlert('Prompts carregados com sucesso!', 'success');
      } else {
        throw new Error('Falha ao carregar prompts');
      }
    } catch (error) {
      console.error('Erro ao carregar prompts:', error);
      showAlert('Erro ao carregar prompts', 'error');
    } finally {
      setLoading(false);
    }
  };

  const savePrompt = async (agentType, promptType, promptText, description) => {
    try {
      const response = await fetch('/api/prompts', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agent_type: agentType,
          prompt_type: promptType,
          prompt_text: promptText,
          description: description
        }),
      });

      if (response.ok) {
        await loadPrompts();
        showAlert('Prompt salvo com sucesso!', 'success');
        return true;
      } else {
        throw new Error('Falha ao salvar prompt');
      }
    } catch (error) {
      console.error('Erro ao salvar prompt:', error);
      showAlert('Erro ao salvar prompt', 'error');
      return false;
    }
  };

  const createPrompt = async () => {
    if (!newPrompt.prompt_type || !newPrompt.prompt_text) {
      showAlert('Preencha todos os campos obrigatórios', 'error');
      return;
    }

    try {
      const response = await fetch('/api/prompts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPrompt),
      });

      if (response.ok) {
        await loadPrompts();
        setNewPrompt({ agent_type: 'tintas', prompt_type: '', prompt_text: '', description: '' });
        setShowNewPromptDialog(false);
        showAlert('Prompt criado com sucesso!', 'success');
      } else {
        throw new Error('Falha ao criar prompt');
      }
    } catch (error) {
      console.error('Erro ao criar prompt:', error);
      showAlert('Erro ao criar prompt', 'error');
    }
  };

  const deletePrompt = async (agentType, promptType) => {
    if (!confirm(`Tem certeza que deseja excluir o prompt ${promptType} do agente ${agentType}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/prompts/${agentType}/${promptType}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        await loadPrompts();
        showAlert('Prompt excluído com sucesso!', 'success');
      } else {
        throw new Error('Falha ao excluir prompt');
      }
    } catch (error) {
      console.error('Erro ao excluir prompt:', error);
      showAlert('Erro ao excluir prompt', 'error');
    }
  };

  const handleEditPrompt = (agentType, promptType, promptData) => {
    setEditingPrompt({
      agent_type: agentType,
      prompt_type: promptType,
      prompt_text: promptData.text,
      description: promptData.description || ''
    });
  };

  const handleSaveEdit = async () => {
    if (!editingPrompt) return;

    const success = await savePrompt(
      editingPrompt.agent_type,
      editingPrompt.prompt_type,
      editingPrompt.prompt_text,
      editingPrompt.description
    );

    if (success) {
      setEditingPrompt(null);
    }
  };

  const formatPromptType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getAgentIcon = (agentType) => {
    const agent = agentTypes.find(a => a.value === agentType);
    return agent ? agent.icon : '🤖';
  };

  const getAgentLabel = (agentType) => {
    const agent = agentTypes.find(a => a.value === agentType);
    return agent ? agent.label : agentType;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Gerenciamento de Prompts</h2>
          <p className="text-muted-foreground">
            Configure as mensagens e respostas dos agentes especialistas
          </p>
        </div>
        <div className="flex gap-2">
          <Button onClick={loadPrompts} variant="outline" size="sm" disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Recarregar
          </Button>
          <Dialog open={showNewPromptDialog} onOpenChange={setShowNewPromptDialog}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Novo Prompt
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Criar Novo Prompt</DialogTitle>
                <DialogDescription>
                  Adicione um novo prompt para um agente especialista
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="new-agent-type">Agente</Label>
                  <Select value={newPrompt.agent_type} onValueChange={(value) => 
                    setNewPrompt({ ...newPrompt, agent_type: value, prompt_type: '' })
                  }>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {agentTypes.map((agent) => (
                        <SelectItem key={agent.value} value={agent.value}>
                          {agent.icon} {agent.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="new-prompt-type">Tipo do Prompt</Label>
                  <Select value={newPrompt.prompt_type} onValueChange={(value) => 
                    setNewPrompt({ ...newPrompt, prompt_type: value })
                  }>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o tipo" />
                    </SelectTrigger>
                    <SelectContent>
                      {promptTypes[newPrompt.agent_type]?.map((type) => (
                        <SelectItem key={type} value={type}>
                          {formatPromptType(type)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="new-description">Descrição</Label>
                  <Input
                    id="new-description"
                    value={newPrompt.description}
                    onChange={(e) => setNewPrompt({ ...newPrompt, description: e.target.value })}
                    placeholder="Descrição do prompt"
                  />
                </div>
                <div>
                  <Label htmlFor="new-prompt-text">Texto do Prompt *</Label>
                  <Textarea
                    id="new-prompt-text"
                    value={newPrompt.prompt_text}
                    onChange={(e) => setNewPrompt({ ...newPrompt, prompt_text: e.target.value })}
                    placeholder="Digite o texto do prompt..."
                    rows={6}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNewPromptDialog(false)}>
                  Cancelar
                </Button>
                <Button onClick={createPrompt}>
                  Criar Prompt
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Alert */}
      {alert.show && (
        <Alert className={alert.type === 'error' ? 'border-red-500 bg-red-50' : 
                         alert.type === 'success' ? 'border-green-500 bg-green-50' : ''}>
          <AlertDescription>{alert.message}</AlertDescription>
        </Alert>
      )}

      {/* Tabs por Agente */}
      <Tabs value={selectedAgent} onValueChange={setSelectedAgent}>
        <TabsList className="grid w-full grid-cols-4">
          {agentTypes.map((agent) => (
            <TabsTrigger key={agent.value} value={agent.value} className="flex items-center gap-2">
              <span>{agent.icon}</span>
              <span className="hidden sm:inline">{agent.label}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {agentTypes.map((agent) => (
          <TabsContent key={agent.value} value={agent.value} className="space-y-4">
            <div className="flex items-center gap-2 mb-4">
              <Bot className="h-5 w-5" />
              <h3 className="text-xl font-semibold">{agent.label}</h3>
              <Badge variant="secondary">
                {Object.keys(prompts[agent.value] || {}).length} prompts
              </Badge>
            </div>

            <div className="grid gap-4">
              {Object.entries(prompts[agent.value] || {}).map(([promptType, promptData]) => (
                <Card key={promptType}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <MessageSquare className="h-4 w-4" />
                        <CardTitle className="text-lg">{formatPromptType(promptType)}</CardTitle>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditPrompt(agent.value, promptType, promptData)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => deletePrompt(agent.value, promptType)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    {promptData.description && (
                      <CardDescription>{promptData.description}</CardDescription>
                    )}
                  </CardHeader>
                  <CardContent>
                    {editingPrompt && 
                     editingPrompt.agent_type === agent.value && 
                     editingPrompt.prompt_type === promptType ? (
                      <div className="space-y-4">
                        <div>
                          <Label>Descrição</Label>
                          <Input
                            value={editingPrompt.description}
                            onChange={(e) => setEditingPrompt({
                              ...editingPrompt,
                              description: e.target.value
                            })}
                            placeholder="Descrição do prompt"
                          />
                        </div>
                        <div>
                          <Label>Texto do Prompt</Label>
                          <Textarea
                            value={editingPrompt.prompt_text}
                            onChange={(e) => setEditingPrompt({
                              ...editingPrompt,
                              prompt_text: e.target.value
                            })}
                            rows={6}
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleSaveEdit} size="sm">
                            <Save className="h-4 w-4 mr-2" />
                            Salvar
                          </Button>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => setEditingPrompt(null)}
                          >
                            Cancelar
                          </Button>
                        </div>
                      </div>
                    ) : (
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <pre className="whitespace-pre-wrap text-sm font-mono">
                          {promptData.text}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {Object.keys(prompts[agent.value] || {}).length === 0 && (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Settings className="h-12 w-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">
                    Nenhum prompt configurado
                  </h3>
                  <p className="text-gray-500 text-center mb-4">
                    Este agente ainda não possui prompts configurados.
                  </p>
                  <Button onClick={() => {
                    setNewPrompt({ ...newPrompt, agent_type: agent.value });
                    setShowNewPromptDialog(true);
                  }}>
                    <Plus className="h-4 w-4 mr-2" />
                    Criar Primeiro Prompt
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
};

export default PromptManager;
