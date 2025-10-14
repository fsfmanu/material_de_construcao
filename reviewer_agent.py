"""
Agente Revisor
Responsável por revisar e melhorar as respostas dos agentes especialistas,
garantindo qualidade, precisão e consistência das informações fornecidas.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from openai import OpenAI

class ReviewerAgent:
    def __init__(self):
        """
        Inicializa o agente revisor com OpenAI
        """
        self.agent_type = "revisor"
        self.client = None
        self.model = "gpt-3.5-turbo"  # Modelo padrão
        
        # Configurar cliente OpenAI
        self._setup_openai_client()
        
        # Critérios de qualidade para revisão
        self.quality_criteria = {
            "accuracy": {
                "name": "Precisão Técnica",
                "description": "Informações técnicas corretas e atualizadas",
                "weight": 0.3
            },
            "completeness": {
                "name": "Completude",
                "description": "Resposta aborda todos os aspectos da pergunta",
                "weight": 0.25
            },
            "clarity": {
                "name": "Clareza",
                "description": "Linguagem clara e compreensível para o cliente",
                "weight": 0.2
            },
            "helpfulness": {
                "name": "Utilidade",
                "description": "Resposta é útil e actionable para o cliente",
                "weight": 0.15
            },
            "professionalism": {
                "name": "Profissionalismo",
                "description": "Tom profissional e adequado ao contexto comercial",
                "weight": 0.1
            }
        }
        
        # Histórico de revisões para análise de padrões
        self.review_history = []

    def _setup_openai_client(self):
        """Configura o cliente OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            print("✅ Cliente OpenAI configurado para Revisor")
        else:
            print("⚠️  OPENAI_API_KEY não encontrada. Revisor funcionará em modo limitado.")

    def _is_openai_available(self) -> bool:
        """Verifica se a OpenAI está disponível"""
        return self.client is not None

    def review_response(self, 
                       user_query: str, 
                       agent_response: str, 
                       agent_type: str,
                       search_results: List[Dict] = None) -> Dict[str, Any]:
        """
        Revisa a resposta de um agente especialista
        
        Args:
            user_query: Pergunta original do usuário
            agent_response: Resposta do agente especialista
            agent_type: Tipo do agente (tintas, pisos, etc.)
            search_results: Resultados da busca semântica (opcional)
            
        Returns:
            Análise detalhada da revisão
        """
        review_result = {
            "user_query": user_query,
            "agent_response": agent_response,
            "agent_type": agent_type,
            "timestamp": datetime.now().isoformat(),
            "review_method": "basic_analysis",
            "quality_scores": {},
            "overall_score": 0.0,
            "suggestions": [],
            "approved": True,
            "improved_response": None
        }
        
        # Se OpenAI está disponível, usar análise avançada
        if self._is_openai_available():
            try:
                openai_review = self._review_with_openai(user_query, agent_response, agent_type, search_results)
                if openai_review:
                    review_result.update(openai_review)
                    review_result["review_method"] = "openai_analysis"
            except Exception as e:
                print(f"⚠️  Erro na revisão OpenAI: {e}. Usando análise básica.")
        
        # Análise básica (fallback)
        if review_result["review_method"] == "basic_analysis":
            basic_review = self._basic_review_analysis(user_query, agent_response, agent_type)
            review_result.update(basic_review)
        
        # Salvar no histórico
        self.review_history.append({
            "timestamp": review_result["timestamp"],
            "agent_type": agent_type,
            "overall_score": review_result["overall_score"],
            "approved": review_result["approved"]
        })
        
        return review_result

    def _review_with_openai(self, 
                           user_query: str, 
                           agent_response: str, 
                           agent_type: str,
                           search_results: List[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Usa OpenAI para revisão avançada da resposta
        
        Args:
            user_query: Pergunta do usuário
            agent_response: Resposta do agente
            agent_type: Tipo do agente
            search_results: Resultados da busca
            
        Returns:
            Análise detalhada ou None se falhar
        """
        try:
            # Contexto dos resultados de busca
            search_context = ""
            if search_results:
                search_context = "\nRESULTADOS DA BUSCA UTILIZADOS:\n"
                for i, result in enumerate(search_results[:3], 1):
                    doc = result.get('document', {})
                    search_context += f"{i}. {doc.get('product_name', 'N/A')} - {doc.get('brand', 'N/A')}\n"
            
            # Prompt para revisão
            system_prompt = f"""Você é um revisor especialista em atendimento ao cliente para uma loja de materiais de construção.
Sua função é revisar respostas de agentes especialistas e garantir qualidade, precisão e utilidade.

CRITÉRIOS DE AVALIAÇÃO (0.0 a 1.0):
1. PRECISÃO TÉCNICA (30%): Informações técnicas corretas e atualizadas
2. COMPLETUDE (25%): Resposta aborda todos os aspectos da pergunta
3. CLAREZA (20%): Linguagem clara e compreensível
4. UTILIDADE (15%): Resposta é útil e actionable
5. PROFISSIONALISMO (10%): Tom adequado ao contexto comercial

AGENTE ESPECIALISTA: {agent_type.upper()}

INSTRUÇÕES:
- Avalie cada critério de 0.0 a 1.0
- Calcule score geral ponderado
- Identifique pontos de melhoria
- Sugira melhorias específicas
- Determine se a resposta deve ser aprovada (score >= 0.7)
- Se necessário, forneça versão melhorada

FORMATO DE RESPOSTA (JSON):
{{
    "quality_scores": {{
        "accuracy": 0.0-1.0,
        "completeness": 0.0-1.0,
        "clarity": 0.0-1.0,
        "helpfulness": 0.0-1.0,
        "professionalism": 0.0-1.0
    }},
    "overall_score": 0.0-1.0,
    "approved": true/false,
    "suggestions": ["sugestão 1", "sugestão 2"],
    "improved_response": "versão melhorada (se necessário)"
}}"""

            user_prompt = f"""PERGUNTA DO CLIENTE: "{user_query}"

RESPOSTA DO AGENTE {agent_type.upper()}:
{agent_response}
{search_context}

Revise esta resposta segundo os critérios estabelecidos."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Extrair resposta
            content = response.choices[0].message.content.strip()
            
            # Tentar parsear JSON
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    review_data = json.loads(json_match.group())
                    return review_data
            except json.JSONDecodeError:
                print("⚠️  Erro ao parsear resposta JSON da OpenAI (Revisor)")
            
            return None
            
        except Exception as e:
            print(f"⚠️  Erro na revisão OpenAI: {e}")
            return None

    def _basic_review_analysis(self, user_query: str, agent_response: str, agent_type: str) -> Dict[str, Any]:
        """
        Análise básica de revisão (fallback)
        
        Args:
            user_query: Pergunta do usuário
            agent_response: Resposta do agente
            agent_type: Tipo do agente
            
        Returns:
            Análise básica
        """
        # Análise simples baseada em heurísticas
        response_length = len(agent_response)
        query_length = len(user_query)
        
        # Scores básicos
        quality_scores = {
            "accuracy": 0.8,  # Assumir boa precisão por padrão
            "completeness": min(response_length / 200, 1.0),  # Baseado no tamanho
            "clarity": 0.8 if response_length > 50 else 0.6,  # Respostas muito curtas podem não ser claras
            "helpfulness": 0.8 if "recomend" in agent_response.lower() or "sugir" in agent_response.lower() else 0.7,
            "professionalism": 0.9 if agent_response.startswith(("Olá", "Oi", "Bom dia")) else 0.8
        }
        
        # Score geral ponderado
        overall_score = sum(
            score * self.quality_criteria[criterion]["weight"]
            for criterion, score in quality_scores.items()
        )
        
        # Sugestões básicas
        suggestions = []
        if quality_scores["completeness"] < 0.7:
            suggestions.append("Considere fornecer mais detalhes na resposta")
        if quality_scores["clarity"] < 0.7:
            suggestions.append("Torne a linguagem mais clara e acessível")
        if "preço" in user_query.lower() and "preço" not in agent_response.lower():
            suggestions.append("Considere abordar aspectos de preço mencionados na pergunta")
        
        return {
            "quality_scores": quality_scores,
            "overall_score": round(overall_score, 2),
            "approved": overall_score >= 0.7,
            "suggestions": suggestions,
            "improved_response": None
        }

    def batch_review(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Revisa múltiplas respostas em lote
        
        Args:
            responses: Lista de dicionários com user_query, agent_response, agent_type
            
        Returns:
            Análise consolidada do lote
        """
        batch_results = []
        total_score = 0
        approved_count = 0
        
        for response_data in responses:
            review = self.review_response(
                response_data.get("user_query", ""),
                response_data.get("agent_response", ""),
                response_data.get("agent_type", "unknown"),
                response_data.get("search_results", [])
            )
            
            batch_results.append(review)
            total_score += review["overall_score"]
            if review["approved"]:
                approved_count += 1
        
        return {
            "batch_size": len(responses),
            "reviews": batch_results,
            "summary": {
                "average_score": round(total_score / len(responses), 2) if responses else 0,
                "approval_rate": round(approved_count / len(responses), 2) if responses else 0,
                "approved_count": approved_count,
                "rejected_count": len(responses) - approved_count
            },
            "timestamp": datetime.now().isoformat()
        }

    def get_improvement_suggestions(self, agent_type: str, time_period_days: int = 30) -> Dict[str, Any]:
        """
        Analisa histórico e fornece sugestões de melhoria para um agente
        
        Args:
            agent_type: Tipo do agente
            time_period_days: Período em dias para análise
            
        Returns:
            Sugestões de melhoria baseadas no histórico
        """
        # Filtrar histórico por agente e período
        cutoff_date = datetime.now().timestamp() - (time_period_days * 24 * 60 * 60)
        
        relevant_reviews = [
            review for review in self.review_history
            if (review.get("agent_type") == agent_type and 
                datetime.fromisoformat(review["timestamp"]).timestamp() > cutoff_date)
        ]
        
        if not relevant_reviews:
            return {
                "agent_type": agent_type,
                "period_days": time_period_days,
                "total_reviews": 0,
                "suggestions": ["Não há dados suficientes para análise"]
            }
        
        # Calcular estatísticas
        total_reviews = len(relevant_reviews)
        average_score = sum(r["overall_score"] for r in relevant_reviews) / total_reviews
        approval_rate = sum(1 for r in relevant_reviews if r["approved"]) / total_reviews
        
        # Gerar sugestões baseadas nas estatísticas
        suggestions = []
        
        if average_score < 0.7:
            suggestions.append("Score médio baixo. Revisar qualidade das respostas.")
        if approval_rate < 0.8:
            suggestions.append("Taxa de aprovação baixa. Focar em completude e precisão.")
        if average_score > 0.9:
            suggestions.append("Excelente performance! Manter padrão atual.")
        
        return {
            "agent_type": agent_type,
            "period_days": time_period_days,
            "total_reviews": total_reviews,
            "average_score": round(average_score, 2),
            "approval_rate": round(approval_rate, 2),
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        }

    def get_quality_report(self) -> Dict[str, Any]:
        """
        Gera relatório de qualidade geral
        
        Returns:
            Relatório consolidado de qualidade
        """
        if not self.review_history:
            return {
                "total_reviews": 0,
                "message": "Nenhuma revisão realizada ainda"
            }
        
        # Estatísticas gerais
        total_reviews = len(self.review_history)
        average_score = sum(r["overall_score"] for r in self.review_history) / total_reviews
        approval_rate = sum(1 for r in self.review_history if r["approved"]) / total_reviews
        
        # Estatísticas por agente
        agent_stats = {}
        for review in self.review_history:
            agent = review["agent_type"]
            if agent not in agent_stats:
                agent_stats[agent] = {"count": 0, "total_score": 0, "approved": 0}
            
            agent_stats[agent]["count"] += 1
            agent_stats[agent]["total_score"] += review["overall_score"]
            if review["approved"]:
                agent_stats[agent]["approved"] += 1
        
        # Calcular médias por agente
        for agent, stats in agent_stats.items():
            stats["average_score"] = round(stats["total_score"] / stats["count"], 2)
            stats["approval_rate"] = round(stats["approved"] / stats["count"], 2)
        
        return {
            "total_reviews": total_reviews,
            "overall_average_score": round(average_score, 2),
            "overall_approval_rate": round(approval_rate, 2),
            "agent_statistics": agent_stats,
            "quality_criteria": self.quality_criteria,
            "timestamp": datetime.now().isoformat()
        }

    def clear_history(self):
        """Limpa histórico de revisões"""
        self.review_history.clear()

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Retorna informações do agente revisor
        
        Returns:
            Informações do agente
        """
        return {
            "agent_type": self.agent_type,
            "name": "Agente Revisor",
            "version": "1.0.0",
            "openai_available": self._is_openai_available(),
            "model": self.model if self._is_openai_available() else None,
            "quality_criteria": self.quality_criteria,
            "total_reviews_performed": len(self.review_history),
            "capabilities": [
                "Revisão de qualidade",
                "Análise de precisão técnica",
                "Sugestões de melhoria",
                "Relatórios de performance",
                "Análise de tendências"
            ]
        }

# Instância global do revisor
reviewer_agent = ReviewerAgent()
