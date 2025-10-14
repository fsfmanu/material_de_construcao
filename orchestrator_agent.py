"""
Agente Orquestrador
Responsável por coordenar múltiplos agentes especialistas, identificar qual agente
deve responder a cada consulta e gerenciar fluxos complexos de conversação.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import openai
from openai import OpenAI

class OrchestratorAgent:
    def __init__(self):
        """
        Inicializa o agente orquestrador com OpenAI
        """
        self.agent_type = "orquestrador"
        self.client = None
        self.model = "gpt-3.5-turbo"  # Modelo padrão
        
        # Configurar cliente OpenAI
        self._setup_openai_client()
        
        # Agentes especialistas disponíveis
        self.available_agents = {
            "tintas": {
                "name": "Especialista em Tintas",
                "description": "Especialista em tintas, vernizes, esmaltes, primers, produtos de pintura",
                "keywords": ["tinta", "verniz", "esmalte", "primer", "pintura", "parede", "madeira", "metal", "cor", "cobertura", "demão"],
                "environments": ["parede", "madeira", "metal", "alvenaria", "gesso"],
                "endpoint": "/api/search"
            },
            "pisos": {
                "name": "Especialista em Pisos e Revestimentos", 
                "description": "Especialista em pisos cerâmicos, porcelanatos, laminados, vinílicos, madeira, pedras naturais",
                "keywords": ["piso", "porcelanato", "cerâmica", "laminado", "vinílico", "madeira", "mármore", "granito", "revestimento", "azulejo"],
                "environments": ["chão", "piso", "sala", "cozinha", "banheiro", "quarto", "área externa"],
                "endpoint": "/api/pisos/search"
            }
        }
        
        # Histórico de conversas para contexto
        self.conversation_history = {}

    def _setup_openai_client(self):
        """Configura o cliente OpenAI"""
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            print("✅ Cliente OpenAI configurado")
        else:
            print("⚠️  OPENAI_API_KEY não encontrada. Orquestrador funcionará em modo limitado.")

    def _is_openai_available(self) -> bool:
        """Verifica se a OpenAI está disponível"""
        return self.client is not None

    def identify_intent_and_agent(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Identifica a intenção do usuário e qual agente deve responder
        
        Args:
            user_query: Consulta do usuário
            session_id: ID da sessão para contexto
            
        Returns:
            Dicionário com agente identificado e informações adicionais
        """
        query_lower = user_query.lower()
        
        # Análise baseada em palavras-chave (fallback)
        keyword_scores = {}
        for agent_id, agent_info in self.available_agents.items():
            score = 0
            keywords = agent_info["keywords"]
            environments = agent_info["environments"]
            
            # Pontuação por palavras-chave
            for keyword in keywords:
                if keyword in query_lower:
                    score += 2
            
            # Pontuação por ambientes
            for env in environments:
                if env in query_lower:
                    score += 1
            
            keyword_scores[agent_id] = score
        
        # Se OpenAI está disponível, usar análise avançada
        if self._is_openai_available():
            try:
                openai_analysis = self._analyze_with_openai(user_query, session_id)
                if openai_analysis:
                    return openai_analysis
            except Exception as e:
                print(f"⚠️  Erro na análise OpenAI: {e}. Usando análise por palavras-chave.")
        
        # Análise por palavras-chave (fallback)
        best_agent = max(keyword_scores.items(), key=lambda x: x[1])
        
        if best_agent[1] == 0:
            # Nenhuma palavra-chave encontrada, usar agente padrão
            selected_agent = "tintas"
            confidence = 0.3
            reasoning = "Nenhuma palavra-chave específica encontrada. Direcionando para agente de tintas por padrão."
        else:
            selected_agent = best_agent[0]
            confidence = min(best_agent[1] / 10.0, 1.0)  # Normalizar para 0-1
            reasoning = f"Identificadas {best_agent[1]} palavras-chave relacionadas a {self.available_agents[selected_agent]['name']}"
        
        return {
            "selected_agent": selected_agent,
            "confidence": confidence,
            "reasoning": reasoning,
            "analysis_method": "keyword_matching",
            "all_scores": keyword_scores,
            "requires_multiple_agents": False,
            "additional_context": {}
        }

    def _analyze_with_openai(self, user_query: str, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Usa OpenAI para análise avançada da consulta
        
        Args:
            user_query: Consulta do usuário
            session_id: ID da sessão
            
        Returns:
            Análise detalhada ou None se falhar
        """
        try:
            # Contexto da conversa anterior se disponível
            context = ""
            if session_id and session_id in self.conversation_history:
                recent_messages = self.conversation_history[session_id][-3:]  # Últimas 3 mensagens
                context = "\n".join([f"- {msg}" for msg in recent_messages])
            
            # Prompt para análise
            system_prompt = f"""Você é um orquestrador inteligente para uma loja de materiais de construção.
Sua função é analisar consultas de clientes e determinar qual especialista deve responder.

AGENTES DISPONÍVEIS:
1. TINTAS: Especialista em tintas, vernizes, esmaltes, primers, produtos de pintura
   - Palavras-chave: tinta, verniz, esmalte, primer, pintura, parede, madeira, metal, cor, cobertura, demão
   - Ambientes: parede, madeira, metal, alvenaria, gesso

2. PISOS: Especialista em pisos cerâmicos, porcelanatos, laminados, vinílicos, madeira, pedras naturais
   - Palavras-chave: piso, porcelanato, cerâmica, laminado, vinílico, madeira, mármore, granito, revestimento, azulejo
   - Ambientes: chão, piso, sala, cozinha, banheiro, quarto, área externa

INSTRUÇÕES:
- Analise a consulta e determine qual agente é mais adequado
- Considere o contexto da conversa anterior se fornecido
- Avalie se múltiplos agentes podem ser necessários
- Forneça uma confiança de 0.0 a 1.0
- Explique seu raciocínio

FORMATO DE RESPOSTA (JSON):
{{
    "selected_agent": "tintas" ou "pisos",
    "confidence": 0.0-1.0,
    "reasoning": "explicação detalhada",
    "requires_multiple_agents": true/false,
    "additional_context": {{}}
}}"""

            user_prompt = f"""CONSULTA DO CLIENTE: "{user_query}"

CONTEXTO DA CONVERSA ANTERIOR:
{context if context else "Nenhum contexto anterior"}

Analise esta consulta e determine qual agente especialista deve responder."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extrair resposta
            content = response.choices[0].message.content.strip()
            
            # Tentar parsear JSON
            try:
                # Procurar por JSON na resposta
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    analysis["analysis_method"] = "openai_gpt"
                    return analysis
            except json.JSONDecodeError:
                print("⚠️  Erro ao parsear resposta JSON da OpenAI")
            
            return None
            
        except Exception as e:
            print(f"⚠️  Erro na análise OpenAI: {e}")
            return None

    def route_query(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Roteia a consulta para o agente apropriado
        
        Args:
            user_query: Consulta do usuário
            session_id: ID da sessão
            
        Returns:
            Resultado do roteamento com resposta do agente
        """
        # Identificar agente
        analysis = self.identify_intent_and_agent(user_query, session_id)
        
        # Salvar no histórico
        if session_id:
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = []
            self.conversation_history[session_id].append(f"User: {user_query}")
        
        # Preparar resposta de roteamento
        routing_result = {
            "user_query": user_query,
            "session_id": session_id,
            "routing_analysis": analysis,
            "timestamp": datetime.now().isoformat(),
            "orchestrator_response": self._generate_routing_response(analysis),
            "next_steps": {
                "agent_endpoint": self.available_agents[analysis["selected_agent"]]["endpoint"],
                "agent_name": self.available_agents[analysis["selected_agent"]]["name"],
                "should_forward": analysis["confidence"] > 0.5
            }
        }
        
        return routing_result

    def _generate_routing_response(self, analysis: Dict[str, Any]) -> str:
        """
        Gera resposta explicando o roteamento
        
        Args:
            analysis: Análise do roteamento
            
        Returns:
            Resposta formatada
        """
        agent_name = self.available_agents[analysis["selected_agent"]]["name"]
        confidence = analysis["confidence"]
        
        if confidence > 0.8:
            return f"🎯 Identifiquei que sua consulta é sobre **{agent_name.lower()}**. Vou direcioná-lo para nosso especialista que tem conhecimento aprofundado nesta área."
        elif confidence > 0.5:
            return f"🤔 Sua consulta parece estar relacionada a **{agent_name.lower()}**. Nosso especialista poderá ajudá-lo melhor com essa questão."
        else:
            return f"📋 Vou direcionar sua consulta para nosso **{agent_name}** que poderá analisar melhor sua necessidade e fornecer orientações adequadas."

    def handle_multi_agent_query(self, user_query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Lida com consultas que podem requerer múltiplos agentes
        
        Args:
            user_query: Consulta do usuário
            session_id: ID da sessão
            
        Returns:
            Resposta coordenada de múltiplos agentes
        """
        # Por enquanto, implementação simples
        # Em versões futuras, pode coordenar respostas de múltiplos agentes
        return self.route_query(user_query, session_id)

    def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Retorna informações sobre capacidades dos agentes disponíveis
        
        Returns:
            Dicionário com informações dos agentes
        """
        return {
            "available_agents": self.available_agents,
            "orchestrator_info": {
                "name": "Agente Orquestrador",
                "version": "1.0.0",
                "openai_available": self._is_openai_available(),
                "model": self.model if self._is_openai_available() else None,
                "capabilities": [
                    "Análise de intenção",
                    "Roteamento inteligente",
                    "Coordenação de múltiplos agentes",
                    "Manutenção de contexto"
                ]
            }
        }

    def clear_conversation_history(self, session_id: str = None):
        """
        Limpa histórico de conversa
        
        Args:
            session_id: ID da sessão específica ou None para limpar tudo
        """
        if session_id:
            if session_id in self.conversation_history:
                del self.conversation_history[session_id]
        else:
            self.conversation_history.clear()

    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas das conversas
        
        Returns:
            Estatísticas das conversas
        """
        total_sessions = len(self.conversation_history)
        total_messages = sum(len(messages) for messages in self.conversation_history.values())
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "active_sessions": list(self.conversation_history.keys()),
            "average_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0
        }

# Instância global do orquestrador
orchestrator_agent = OrchestratorAgent()
