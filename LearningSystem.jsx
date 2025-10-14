import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Button } from '@/components/ui/button.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Brain, TrendingUp, MessageSquare, Star, ThumbsUp, ThumbsDown } from 'lucide-react'

const LearningSystem = () => {
  const [interactions, setInteractions] = useState([])
  const [feedback, setFeedback] = useState([])
  const [commonQuestions, setCommonQuestions] = useState([])
  const [newQuestion, setNewQuestion] = useState('')
  const [newAnswer, setNewAnswer] = useState('')

  // Simular dados de aprendizado
  useEffect(() => {
    const mockInteractions = [
      {
        id: 1,
        question: 'Qual tinta usar para banheiro?',
        answer: 'Para banheiros, recomendo tintas laváveis como Coral Super Lavável ou Suvinil com ação antimicrobiana.',
        timestamp: new Date().toISOString(),
        rating: 5,
        category: 'ambiente_especifico'
      },
      {
        id: 2,
        question: 'Como calcular tinta para fachada?',
        answer: 'Para fachadas, use a fórmula: Área = (Largura × Altura × Paredes) - Vãos. Considere rendimento de 12-14 m²/L para tintas premium.',
        timestamp: new Date().toISOString(),
        rating: 4,
        category: 'calculo'
      },
      {
        id: 3,
        question: 'Tinta descascando, o que fazer?',
        answer: 'Descascamento indica má preparação. Remova camadas soltas, trate umidade se houver, aplique primer adequado.',
        timestamp: new Date().toISOString(),
        rating: 5,
        category: 'problema_tecnico'
      }
    ]

    const mockFeedback = [
      { id: 1, interactionId: 1, rating: 5, comment: 'Resposta muito útil!', timestamp: new Date().toISOString() },
      { id: 2, interactionId: 2, rating: 4, comment: 'Boa explicação, mas poderia ter mais detalhes', timestamp: new Date().toISOString() },
      { id: 3, interactionId: 3, rating: 5, comment: 'Excelente diagnóstico!', timestamp: new Date().toISOString() }
    ]

    const mockCommonQuestions = [
      { question: 'Qual tinta usar para banheiro?', frequency: 45, category: 'ambiente_especifico' },
      { question: 'Como calcular quantidade de tinta?', frequency: 38, category: 'calculo' },
      { question: 'Tinta descascando, o que fazer?', frequency: 32, category: 'problema_tecnico' },
      { question: 'Diferença entre tinta premium e econômica?', frequency: 28, category: 'produto' },
      { question: 'Posso pintar madeira com tinta acrílica?', frequency: 24, category: 'superficie' }
    ]

    setInteractions(mockInteractions)
    setFeedback(mockFeedback)
    setCommonQuestions(mockCommonQuestions)
  }, [])

  const addNewKnowledge = () => {
    if (!newQuestion.trim() || !newAnswer.trim()) return

    const newInteraction = {
      id: interactions.length + 1,
      question: newQuestion,
      answer: newAnswer,
      timestamp: new Date().toISOString(),
      rating: 0,
      category: 'manual_input'
    }

    setInteractions([...interactions, newInteraction])
    setNewQuestion('')
    setNewAnswer('')
  }

  const getCategoryColor = (category) => {
    const colors = {
      'ambiente_especifico': 'bg-blue-100 text-blue-800',
      'calculo': 'bg-green-100 text-green-800',
      'problema_tecnico': 'bg-red-100 text-red-800',
      'produto': 'bg-purple-100 text-purple-800',
      'superficie': 'bg-orange-100 text-orange-800',
      'manual_input': 'bg-gray-100 text-gray-800'
    }
    return colors[category] || 'bg-gray-100 text-gray-800'
  }

  const averageRating = interactions.length > 0 
    ? (interactions.reduce((sum, int) => sum + int.rating, 0) / interactions.length).toFixed(1)
    : 0

  return (
    <div className="space-y-6">
      {/* Métricas de Aprendizado */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-2xl font-bold">{interactions.length}</p>
                <p className="text-sm text-gray-600">Interações</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Star className="h-5 w-5 text-yellow-600" />
              <div>
                <p className="text-2xl font-bold">{averageRating}</p>
                <p className="text-sm text-gray-600">Avaliação Média</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-2xl font-bold">{feedback.length}</p>
                <p className="text-sm text-gray-600">Feedbacks</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-2xl font-bold">{commonQuestions.length}</p>
                <p className="text-sm text-gray-600">Padrões Identificados</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Perguntas Mais Frequentes */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Perguntas Mais Frequentes
            </CardTitle>
            <CardDescription>
              Padrões identificados nas interações dos usuários
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {commonQuestions.map((item, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{item.question}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className={getCategoryColor(item.category)}>
                        {item.category.replace('_', ' ')}
                      </Badge>
                      <span className="text-xs text-gray-500">{item.frequency} vezes</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Adicionar Novo Conhecimento */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Adicionar Conhecimento
            </CardTitle>
            <CardDescription>
              Expanda a base de conhecimento do agente
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Nova Pergunta</label>
              <Input
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                placeholder="Ex: Como pintar sobre azulejo?"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Resposta Técnica</label>
              <Textarea
                value={newAnswer}
                onChange={(e) => setNewAnswer(e.target.value)}
                placeholder="Forneça uma resposta técnica detalhada..."
                rows={4}
              />
            </div>
            <Button onClick={addNewKnowledge} className="w-full">
              Adicionar ao Conhecimento
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Histórico de Interações */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            Histórico de Interações
          </CardTitle>
          <CardDescription>
            Registro das consultas e avaliações dos usuários
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {interactions.map((interaction) => (
              <div key={interaction.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <p className="font-medium text-sm mb-1">{interaction.question}</p>
                    <Badge className={getCategoryColor(interaction.category)}>
                      {interaction.category.replace('_', ' ')}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${
                          i < interaction.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-2">{interaction.answer}</p>
                <p className="text-xs text-gray-400">
                  {new Date(interaction.timestamp).toLocaleString('pt-BR')}
                </p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Sistema de Feedback */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ThumbsUp className="h-5 w-5" />
            Sistema de Feedback
          </CardTitle>
          <CardDescription>
            Avaliações e comentários dos usuários para melhoria contínua
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {feedback.map((item) => {
              const interaction = interactions.find(int => int.id === item.interactionId)
              return (
                <div key={item.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${
                          i < item.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{interaction?.question}</p>
                    <p className="text-sm text-gray-600 mt-1">{item.comment}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(item.timestamp).toLocaleString('pt-BR')}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default LearningSystem
