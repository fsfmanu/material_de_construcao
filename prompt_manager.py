"""
Gerenciador de Prompts para Agentes Especialistas
Permite carregar, atualizar e gerenciar prompts armazenados no Supabase
"""

import json
from typing import Dict, List, Optional, Any
from supabase_client import supabase_manager

class PromptManager:
    def __init__(self):
        self.supabase = supabase_manager
        self._cache = {}  # Cache local dos prompts
        self._cache_loaded = False
    
    def load_prompts_cache(self, agent_type: str = None) -> None:
        """Carrega prompts do Supabase para o cache local"""
        try:
            if self.supabase.is_connected():
                # Carregar do Supabase
                if agent_type:
                    prompts = self.supabase.get_agent_prompts(agent_type)
                else:
                    prompts = self.supabase.get_all_agent_prompts()
                
                # Organizar prompts por agent_type e prompt_type
                for prompt in prompts:
                    agent_key = prompt['agent_type']
                    prompt_key = prompt['prompt_type']
                    
                    if agent_key not in self._cache:
                        self._cache[agent_key] = {}
                    
                    self._cache[agent_key][prompt_key] = {
                        'id': prompt['id'],
                        'text': prompt['prompt_text'],
                        'description': prompt['description'],
                        'is_active': prompt['is_active']
                    }
                
                self._cache_loaded = True
                print(f"✅ Prompts carregados do Supabase: {len(prompts)} prompts")
            else:
                # Usar prompts padrão quando Supabase não está conectado
                self._load_default_prompts()
                print("⚠️  Usando prompts padrão (Supabase não conectado)")
        
        except Exception as e:
            print(f"❌ Erro ao carregar prompts: {e}")
            self._load_default_prompts()
    
    def _load_default_prompts(self) -> None:
        """Carrega prompts padrão quando Supabase não está disponível"""
        self._cache = {
            'tintas': {
                'initial_greeting': {
                    'text': 'Olá! Sou seu especialista em tintas com 20 anos de experiência. Posso ajudá-lo com recomendações de produtos, cálculos de quantidade, orçamentos e solução de problemas de pintura.',
                    'description': 'Saudação inicial do agente de tintas',
                    'is_active': True
                },
                'product_recommendation_intro': {
                    'text': 'Encontrei {count} produto(s) relevante(s) para sua consulta:',
                    'description': 'Introdução para recomendações de produtos',
                    'is_active': True
                },
                'budget_request': {
                    'text': '''Para elaborar um orçamento preciso, preciso saber:
1. Tipo de projeto (residencial/comercial/industrial)
2. Superfície a pintar (parede, madeira, metal, etc.)
3. Área em m²
4. Condições do ambiente (interno/externo, umidade)
5. Acabamento desejado (fosco, acetinado, brilhante)

Você pode me fornecer essas informações?''',
                    'description': 'Solicitação de informações para orçamento',
                    'is_active': True
                },
                'paint_problem_diagnosis': {
                    'text': '''Problemas de descascamento geralmente indicam:
1. Superfície mal preparada (80% dos casos)
2. Presença de umidade
3. Incompatibilidade química entre produtos

**Recomendo:** Remoção completa das camadas soltas, tratamento da umidade na fonte e aplicação de primer adequado.''',
                    'description': 'Diagnóstico para problemas de pintura',
                    'is_active': True
                },
                'calculation_help': {
                    'text': '''Para calcular a tinta necessária:
- Área Total = (Largura × Altura × Paredes) - Vãos
- Litros = Área ÷ Rendimento ÷ Demãos + 10% para perdas

Qual a área que você precisa pintar?''',
                    'description': 'Ajuda para cálculos de quantidade',
                    'is_active': True
                },
                'no_results_found': {
                    'text': '''Não encontrei produtos específicos para sua consulta, mas posso ajudá-lo com:

🎨 **Recomendações de produtos**
📊 **Cálculo de materiais**
🔧 **Solução de problemas**
💰 **Orçamentos personalizados**
🌈 **Escolha de cores e sistemas de pintura**

Qual sua necessidade específica?''',
                    'description': 'Resposta quando não há resultados na busca',
                    'is_active': True
                },
                'error_message': {
                    'text': 'Desculpe, ocorreu um erro técnico. Por favor, tente novamente ou reformule sua pergunta. Se o problema persistir, entre em contato com nosso suporte.',
                    'description': 'Mensagem de erro genérica',
                    'is_active': True
                }
            },
            'orquestrador': {
                'initial_greeting': {
                    'text': 'Olá! Sou seu assistente especializado em materiais de construção. Posso ajudá-lo com tintas, pisos, revestimentos e muito mais. Como posso ajudá-lo hoje?',
                    'description': 'Saudação inicial do agente orquestrador',
                    'is_active': True
                },
                'routing_message': {
                    'text': 'Vou conectá-lo com nosso especialista em {specialty} para melhor atendê-lo.',
                    'description': 'Mensagem ao rotear para especialista',
                    'is_active': True
                }
            },
            'revisor': {
                'quality_check_intro': {
                    'text': 'Revisando a resposta para garantir precisão e clareza...',
                    'description': 'Introdução do processo de revisão',
                    'is_active': True
                }
            }
        }
        self._cache_loaded = True
    
    def get_prompt(self, agent_type: str, prompt_type: str, **kwargs) -> str:
        """
        Obtém um prompt específico e aplica formatação se necessário
        
        Args:
            agent_type: Tipo do agente (tintas, pisos, orquestrador, revisor)
            prompt_type: Tipo do prompt (initial_greeting, product_recommendation, etc.)
            **kwargs: Variáveis para formatação do prompt
        
        Returns:
            Texto do prompt formatado
        """
        if not self._cache_loaded:
            self.load_prompts_cache()
        
        try:
            prompt_data = self._cache.get(agent_type, {}).get(prompt_type)
            
            if not prompt_data or not prompt_data.get('is_active', True):
                # Fallback para prompt genérico
                return f"Olá! Como posso ajudá-lo hoje? (Prompt {agent_type}/{prompt_type} não encontrado)"
            
            prompt_text = prompt_data['text']
            
            # Aplicar formatação se houver kwargs
            if kwargs:
                try:
                    prompt_text = prompt_text.format(**kwargs)
                except KeyError as e:
                    print(f"⚠️  Variável não encontrada no prompt {agent_type}/{prompt_type}: {e}")
            
            return prompt_text
        
        except Exception as e:
            print(f"❌ Erro ao obter prompt {agent_type}/{prompt_type}: {e}")
            return "Olá! Como posso ajudá-lo hoje?"
    
    def get_all_prompts(self, agent_type: str = None) -> Dict[str, Any]:
        """
        Obtém todos os prompts de um agente ou de todos os agentes
        
        Args:
            agent_type: Tipo do agente (opcional, se None retorna todos)
        
        Returns:
            Dicionário com os prompts
        """
        if not self._cache_loaded:
            self.load_prompts_cache()
        
        if agent_type:
            return self._cache.get(agent_type, {})
        else:
            return self._cache
    
    def update_prompt(self, agent_type: str, prompt_type: str, prompt_text: str, description: str = None) -> bool:
        """
        Atualiza um prompt no Supabase e no cache local
        
        Args:
            agent_type: Tipo do agente
            prompt_type: Tipo do prompt
            prompt_text: Novo texto do prompt
            description: Nova descrição (opcional)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        try:
            if self.supabase.is_connected():
                # Atualizar no Supabase
                success = self.supabase.update_agent_prompt(agent_type, prompt_type, prompt_text, description)
                
                if success:
                    # Atualizar cache local
                    if agent_type not in self._cache:
                        self._cache[agent_type] = {}
                    
                    if prompt_type not in self._cache[agent_type]:
                        self._cache[agent_type][prompt_type] = {}
                    
                    self._cache[agent_type][prompt_type]['text'] = prompt_text
                    if description:
                        self._cache[agent_type][prompt_type]['description'] = description
                    
                    print(f"✅ Prompt {agent_type}/{prompt_type} atualizado")
                    return True
                else:
                    print(f"❌ Falha ao atualizar prompt {agent_type}/{prompt_type} no Supabase")
                    return False
            else:
                # Atualizar apenas no cache local quando Supabase não está conectado
                if agent_type not in self._cache:
                    self._cache[agent_type] = {}
                
                if prompt_type not in self._cache[agent_type]:
                    self._cache[agent_type][prompt_type] = {}
                
                self._cache[agent_type][prompt_type]['text'] = prompt_text
                if description:
                    self._cache[agent_type][prompt_type]['description'] = description
                
                print(f"⚠️  Prompt {agent_type}/{prompt_type} atualizado apenas localmente (Supabase não conectado)")
                return True
        
        except Exception as e:
            print(f"❌ Erro ao atualizar prompt {agent_type}/{prompt_type}: {e}")
            return False
    
    def create_prompt(self, agent_type: str, prompt_type: str, prompt_text: str, description: str = None) -> bool:
        """
        Cria um novo prompt no Supabase e no cache local
        
        Args:
            agent_type: Tipo do agente
            prompt_type: Tipo do prompt
            prompt_text: Texto do prompt
            description: Descrição do prompt (opcional)
        
        Returns:
            True se criado com sucesso, False caso contrário
        """
        try:
            if self.supabase.is_connected():
                # Criar no Supabase
                prompt_id = self.supabase.create_agent_prompt(agent_type, prompt_type, prompt_text, description)
                
                if prompt_id:
                    # Atualizar cache local
                    if agent_type not in self._cache:
                        self._cache[agent_type] = {}
                    
                    self._cache[agent_type][prompt_type] = {
                        'id': prompt_id,
                        'text': prompt_text,
                        'description': description,
                        'is_active': True
                    }
                    
                    print(f"✅ Prompt {agent_type}/{prompt_type} criado")
                    return True
                else:
                    print(f"❌ Falha ao criar prompt {agent_type}/{prompt_type} no Supabase")
                    return False
            else:
                # Criar apenas no cache local quando Supabase não está conectado
                if agent_type not in self._cache:
                    self._cache[agent_type] = {}
                
                self._cache[agent_type][prompt_type] = {
                    'text': prompt_text,
                    'description': description,
                    'is_active': True
                }
                
                print(f"⚠️  Prompt {agent_type}/{prompt_type} criado apenas localmente (Supabase não conectado)")
                return True
        
        except Exception as e:
            print(f"❌ Erro ao criar prompt {agent_type}/{prompt_type}: {e}")
            return False
    
    def delete_prompt(self, agent_type: str, prompt_type: str) -> bool:
        """
        Remove um prompt do Supabase e do cache local
        
        Args:
            agent_type: Tipo do agente
            prompt_type: Tipo do prompt
        
        Returns:
            True se removido com sucesso, False caso contrário
        """
        try:
            if self.supabase.is_connected():
                # Remover do Supabase
                success = self.supabase.delete_agent_prompt(agent_type, prompt_type)
                
                if success:
                    # Remover do cache local
                    if agent_type in self._cache and prompt_type in self._cache[agent_type]:
                        del self._cache[agent_type][prompt_type]
                    
                    print(f"✅ Prompt {agent_type}/{prompt_type} removido")
                    return True
                else:
                    print(f"❌ Falha ao remover prompt {agent_type}/{prompt_type} do Supabase")
                    return False
            else:
                # Remover apenas do cache local quando Supabase não está conectado
                if agent_type in self._cache and prompt_type in self._cache[agent_type]:
                    del self._cache[agent_type][prompt_type]
                
                print(f"⚠️  Prompt {agent_type}/{prompt_type} removido apenas localmente (Supabase não conectado)")
                return True
        
        except Exception as e:
            print(f"❌ Erro ao remover prompt {agent_type}/{prompt_type}: {e}")
            return False
    
    def reload_cache(self) -> None:
        """Recarrega o cache de prompts do Supabase"""
        self._cache = {}
        self._cache_loaded = False
        self.load_prompts_cache()

# Instância global do gerenciador de prompts
prompt_manager = PromptManager()
