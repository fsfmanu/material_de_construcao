import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Edit,
  Eye,
  Clock,
  Star,
  TrendingUp,
  FileText
} from 'lucide-react';

const ReviewerPanel = ({ apiUrl = 'http://localhost:5000' }) => {
  const [pendingReviews, setPendingReviews] = useState([]);
  const [reviewHistory, setReviewHistory] = useState([]);
  const [selectedResponse, setSelectedResponse] = useState(null);
  const [reviewComment, setReviewComment] = useState('');
  const [isReviewing, setIsReviewing] = useState(false);
  const [reviewStats, setReviewStats] = useState({});

  useEffect(() => {
    // Simular dados de revisões pendentes
    setPendingReviews([
      {
        id: 1,
        query: "Qual a melhor tinta para parede externa?",
        agent: "tintas",
        response: "Para paredes externas, recomendo a Coral Acrílica Premium. Ela oferece excelente resistência às intempéries, proteção UV e durabilidade de até 8 anos. Sua formulação especial impede o crescimento de fungos e bactérias.",
        confidence: 0.92,
        timestamp: "2024-01-15 14:30:22",
        priority: "medium",
        user_context: "Cliente residencial",
        products_mentioned: ["Coral Acrílica Premium"],
        technical_accuracy: null,
        completeness: null,
        clarity: null
      },
      {
        id: 2,
        query: "Preciso de piso para cozinha que seja fácil de limpar",
        agent: "pisos",
        response: "Para cozinha, recomendo porcelanato esmaltado ou piso vinílico SPC. O porcelanato oferece alta resistência e facilidade de limpeza, enquanto o vinílico é 100% impermeável e antibacteriano. Ambos são ideais para áreas molhadas.",
        confidence: 0.88,
        timestamp: "2024-01-15 14:25:15",
        priority: "high",
        user_context: "Cliente comercial",
        products_mentioned: ["Porcelanato Esmaltado", "Piso Vinílico SPC"],
        technical_accuracy: null,
        completeness: null,
        clarity: null
      },
      {
        id: 3,
        query: "Orçamento para pintar casa de 120m²",
        agent: "orquestrador",
        response: "Para uma casa de 120m², considerando 2 demãos de tinta acrílica premium, você precisará de aproximadamente 24 litros de tinta. O custo estimado fica entre R$ 800 a R$ 1.200, incluindo primer e materiais de aplicação.",
        confidence: 0.75,
        timestamp: "2024-01-15 14:20:08",
        priority: "low",
        user_context: "Cliente residencial",
        products_mentioned: ["Tinta Acrílica Premium", "Primer"],
        technical_accuracy: null,
        completeness: null,
        clarity: null
      }
    ]);

    // Simular histórico de revisões
    setReviewHistory([
      {
        id: 101,
        query: "Tinta para madeira externa",
        agent: "tintas",
        review_status: "approved",
        reviewer_comment: "Resposta técnica precisa e completa",
        reviewed_at: "2024-01-15 13:45:00",
        scores: { technical_accuracy: 5, completeness: 5, clarity: 4 }
      },
      {
        id: 102,
        query: "Piso laminado vs vinílico",
        agent: "pisos",
        review_status: "approved_with_changes",
        reviewer_comment: "Boa comparação, mas faltou mencionar custo-benefício",
        reviewed_at: "2024-01-15 13:30:00",
        scores: { technical_accuracy: 4, completeness: 3, clarity: 5 }
      },
      {
        id: 103,
        query: "Cores de tinta para quarto infantil",
        agent: "tintas",
        review_status: "rejected",
        reviewer_comment: "Resposta muito genérica, faltou considerar aspectos psicológicos das cores",
        reviewed_at: "2024-01-15 13:15:00",
        scores: { technical_accuracy: 3, completeness: 2, clarity: 4 }
      }
    ]);

    // Simular estatísticas
    setReviewStats({
      total_reviews: 156,
      approved: 89,
      approved_with_changes: 45,
      rejected: 22,
      average_score: 4.2,
      pending_count: 3
    });
  }, []);

  const submitReview = async (responseId, status, scores) => {
    setIsReviewing(true);

    try {
      const response = await fetch(`${apiUrl}/api/reviewer/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          response_id: responseId,
          review_status: status,
          scores: scores,
          comment: reviewComment,
          reviewer_id: 'admin'
        }),
      });

      const data = await response.json();

      if (data.success) {
        // Remover da lista de pendentes
        setPendingReviews(prev => prev.filter(item => item.id !== responseId));
        
        // Adicionar ao histórico
        const reviewedItem = pendingReviews.find(item => item.id === responseId);
        if (reviewedItem) {
          setReviewHistory(prev => [{
            id: responseId,
            query: reviewedItem.query,
            agent: reviewedItem.agent,
            review_status: status,
            reviewer_comment: reviewComment,
            reviewed_at: new Date().toISOString(),
            scores: scores
          }, ...prev]);
        }

        setSelectedResponse(null);
        setReviewComment('');
        
        alert('Revisão enviada com sucesso!');
      }
    } catch (error) {
      console.error('Erro ao enviar revisão:', error);
      alert('Erro ao enviar revisão. Tente novamente.');
    }

    setIsReviewing(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-500';
      case 'approved_with_changes': return 'bg-yellow-500';
      case 'rejected': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved': return <CheckCircle className="w-4 h-4" />;
      case 'approved_with_changes': return <AlertTriangle className="w-4 h-4" />;
      case 'rejected': return <XCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-green-500 bg-green-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const getAgentIcon = (agent) => {
    switch (agent) {
      case 'tintas': return '🎨';
      case 'pisos': return '🏠';
      case 'orquestrador': return '🎭';
      default: return '🤖';
    }
  };

  const StarRating = ({ rating, onRatingChange, label }) => {
    return (
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium w-32">{label}:</span>
        <div className="flex gap-1">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              onClick={() => onRatingChange(star)}
              className={`w-5 h-5 ${star <= rating ? 'text-yellow-500' : 'text-gray-300'}`}
            >
              <Star className="w-full h-full fill-current" />
            </button>
          ))}
        </div>
        <span className="text-sm text-gray-600">({rating}/5)</span>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          ✅ Revisor de Agentes
        </h2>
        <p className="text-gray-600">
          Revisa e aprova respostas dos agentes especialistas para garantir qualidade
        </p>
      </div>

      <Tabs defaultValue="pending" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="pending" className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Pendentes ({pendingReviews.length})
          </TabsTrigger>
          <TabsTrigger value="review" className="flex items-center gap-2">
            <Eye className="w-4 h-4" />
            Revisar
          </TabsTrigger>
          <TabsTrigger value="history" className="flex items-center gap-2">
            <FileText className="w-4 h-4" />
            Histórico
          </TabsTrigger>
          <TabsTrigger value="stats" className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Estatísticas
          </TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5" />
                Respostas Pendentes de Revisão
              </CardTitle>
              <CardDescription>
                Respostas dos agentes aguardando aprovação
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {pendingReviews.map((item) => (
                  <div key={item.id} className={`border-l-4 rounded-lg p-4 ${getPriorityColor(item.priority)}`}>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getAgentIcon(item.agent)}</span>
                        <Badge variant="outline" className="capitalize">{item.agent}</Badge>
                        <Badge variant="secondary">{item.priority} prioridade</Badge>
                        <Badge variant="outline">
                          {Math.round(item.confidence * 100)}% confiança
                        </Badge>
                      </div>
                      <Button 
                        size="sm" 
                        onClick={() => setSelectedResponse(item)}
                        variant="outline"
                      >
                        <Eye className="w-4 h-4 mr-1" />
                        Revisar
                      </Button>
                    </div>
                    
                    <div className="space-y-2">
                      <div>
                        <p className="text-sm font-medium text-gray-700">Consulta:</p>
                        <p className="text-sm bg-white p-2 rounded border">{item.query}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm font-medium text-gray-700">Resposta:</p>
                        <p className="text-sm bg-white p-2 rounded border">{item.response}</p>
                      </div>
                      
                      {item.products_mentioned.length > 0 && (
                        <div>
                          <p className="text-sm font-medium text-gray-700">Produtos Mencionados:</p>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {item.products_mentioned.map((product, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {product}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Contexto: {item.user_context}</span>
                        <span>{new Date(item.timestamp).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="review" className="space-y-4">
          {selectedResponse ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Edit className="w-5 h-5" />
                  Revisando Resposta #{selectedResponse.id}
                </CardTitle>
                <CardDescription>
                  Avalie a qualidade da resposta do agente {selectedResponse.agent}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Consulta Original:</p>
                      <p className="text-sm bg-gray-50 p-3 rounded border">{selectedResponse.query}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-2">Contexto:</p>
                      <div className="space-y-1">
                        <p className="text-sm">Agente: <Badge variant="outline">{selectedResponse.agent}</Badge></p>
                        <p className="text-sm">Confiança: <Badge variant="secondary">{Math.round(selectedResponse.confidence * 100)}%</Badge></p>
                        <p className="text-sm">Usuário: {selectedResponse.user_context}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm font-medium text-gray-700 mb-2">Resposta do Agente:</p>
                    <div className="bg-blue-50 p-4 rounded border">
                      <p className="text-sm">{selectedResponse.response}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <h3 className="font-semibold">Avaliação da Resposta:</h3>
                    
                    <div className="space-y-3">
                      <StarRating 
                        rating={selectedResponse.technical_accuracy || 0}
                        onRatingChange={(rating) => setSelectedResponse({
                          ...selectedResponse, 
                          technical_accuracy: rating
                        })}
                        label="Precisão Técnica"
                      />
                      
                      <StarRating 
                        rating={selectedResponse.completeness || 0}
                        onRatingChange={(rating) => setSelectedResponse({
                          ...selectedResponse, 
                          completeness: rating
                        })}
                        label="Completude"
                      />
                      
                      <StarRating 
                        rating={selectedResponse.clarity || 0}
                        onRatingChange={(rating) => setSelectedResponse({
                          ...selectedResponse, 
                          clarity: rating
                        })}
                        label="Clareza"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Comentários da Revisão:
                    </label>
                    <Textarea
                      value={reviewComment}
                      onChange={(e) => setReviewComment(e.target.value)}
                      placeholder="Adicione comentários sobre a qualidade da resposta, sugestões de melhoria, etc."
                      rows={4}
                    />
                  </div>
                  
                  <div className="flex gap-3">
                    <Button 
                      onClick={() => submitReview(
                        selectedResponse.id, 
                        'approved',
                        {
                          technical_accuracy: selectedResponse.technical_accuracy || 0,
                          completeness: selectedResponse.completeness || 0,
                          clarity: selectedResponse.clarity || 0
                        }
                      )}
                      disabled={isReviewing}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Aprovar
                    </Button>
                    
                    <Button 
                      onClick={() => submitReview(
                        selectedResponse.id, 
                        'approved_with_changes',
                        {
                          technical_accuracy: selectedResponse.technical_accuracy || 0,
                          completeness: selectedResponse.completeness || 0,
                          clarity: selectedResponse.clarity || 0
                        }
                      )}
                      disabled={isReviewing}
                      variant="outline"
                      className="border-yellow-500 text-yellow-700 hover:bg-yellow-50"
                    >
                      <AlertTriangle className="w-4 h-4 mr-2" />
                      Aprovar com Alterações
                    </Button>
                    
                    <Button 
                      onClick={() => submitReview(
                        selectedResponse.id, 
                        'rejected',
                        {
                          technical_accuracy: selectedResponse.technical_accuracy || 0,
                          completeness: selectedResponse.completeness || 0,
                          clarity: selectedResponse.clarity || 0
                        }
                      )}
                      disabled={isReviewing}
                      variant="outline"
                      className="border-red-500 text-red-700 hover:bg-red-50"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Rejeitar
                    </Button>
                    
                    <Button 
                      onClick={() => setSelectedResponse(null)}
                      variant="ghost"
                    >
                      Cancelar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma resposta selecionada</h3>
                <p className="text-gray-600">Selecione uma resposta da aba "Pendentes" para começar a revisão</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Histórico de Revisões
              </CardTitle>
              <CardDescription>
                Revisões anteriores realizadas no sistema
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {reviewHistory.map((review) => (
                  <div key={review.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getAgentIcon(review.agent)}</span>
                        <Badge variant="outline" className="capitalize">{review.agent}</Badge>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded text-white text-xs ${getStatusColor(review.review_status)}`}>
                          {getStatusIcon(review.review_status)}
                          <span className="capitalize">{review.review_status.replace('_', ' ')}</span>
                        </div>
                      </div>
                      <span className="text-sm text-gray-500">
                        {new Date(review.reviewed_at).toLocaleString()}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-2">{review.query}</p>
                    
                    {review.reviewer_comment && (
                      <p className="text-sm bg-gray-50 p-2 rounded border italic">
                        "{review.reviewer_comment}"
                      </p>
                    )}
                    
                    <div className="flex items-center gap-4 mt-3 text-xs text-gray-600">
                      <span>Técnica: {review.scores.technical_accuracy}/5</span>
                      <span>Completude: {review.scores.completeness}/5</span>
                      <span>Clareza: {review.scores.clarity}/5</span>
                      <span>Média: {((review.scores.technical_accuracy + review.scores.completeness + review.scores.clarity) / 3).toFixed(1)}/5</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Total Revisões</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {reviewStats.total_reviews}
                </div>
                <p className="text-sm text-gray-600">Revisões realizadas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Taxa de Aprovação</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {reviewStats.total_reviews ? 
                    Math.round((reviewStats.approved / reviewStats.total_reviews) * 100) : 0}%
                </div>
                <p className="text-sm text-gray-600">Respostas aprovadas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Nota Média</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {reviewStats.average_score}/5
                </div>
                <p className="text-sm text-gray-600">Qualidade das respostas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-lg">Pendentes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {reviewStats.pending_count}
                </div>
                <p className="text-sm text-gray-600">Aguardando revisão</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Distribuição de Status</CardTitle>
              <CardDescription>
                Breakdown das revisões por status de aprovação
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="font-medium w-32">Aprovadas</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${(reviewStats.approved / reviewStats.total_reviews) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium w-12">{reviewStats.approved}</span>
                </div>

                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                  <span className="font-medium w-32">Com Alterações</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-yellow-500 h-2 rounded-full" 
                      style={{ width: `${(reviewStats.approved_with_changes / reviewStats.total_reviews) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium w-12">{reviewStats.approved_with_changes}</span>
                </div>

                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 text-red-500" />
                  <span className="font-medium w-32">Rejeitadas</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full" 
                      style={{ width: `${(reviewStats.rejected / reviewStats.total_reviews) * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium w-12">{reviewStats.rejected}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ReviewerPanel;
