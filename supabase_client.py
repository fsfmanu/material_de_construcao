import os
from supabase import create_client, Client
from typing import Optional, Dict, List, Any
import json
from datetime import datetime

class SupabaseManager:
    def __init__(self):
        # Configurações do Supabase (definir como variáveis de ambiente)
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY', '')
        
        if not self.supabase_url or not self.supabase_key:
            print("⚠️  Configurações do Supabase não encontradas. Usando modo local.")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.supabase_url, self.supabase_key)
                print("✅ Conectado ao Supabase com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao conectar com Supabase: {e}")
                self.client = None
    
    def is_connected(self) -> bool:
        """Verifica se está conectado ao Supabase"""
        return self.client is not None
    
    # PRODUTOS
    def get_products(self, active_only: bool = True) -> List[Dict]:
        """Busca produtos do Supabase"""
        if not self.client:
            return []
        
        try:
            query = self.client.table('products').select('*')
            if active_only:
                query = query.eq('active', True)
            
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar produtos: {e}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Busca produto específico por ID"""
        if not self.client:
            return None
        
        try:
            response = self.client.table('products').select('*').eq('product_id', product_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar produto {product_id}: {e}")
            return None
    
    def create_product(self, product_data: Dict) -> Optional[str]:
        """Cria novo produto"""
        if not self.client:
            return None
        
        try:
            response = self.client.table('products').insert(product_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao criar produto: {e}")
            return None
    
    def update_product(self, product_id: str, updates: Dict) -> bool:
        """Atualiza produto existente"""
        if not self.client:
            return False
        
        try:
            response = self.client.table('products').update(updates).eq('product_id', product_id).execute()
            return len(response.data) > 0
        except Exception as e:
            print(f"Erro ao atualizar produto {product_id}: {e}")
            return False
    
    def delete_product(self, product_id: str) -> bool:
        """Remove produto (marca como inativo)"""
        return self.update_product(product_id, {'active': False})
    
    # CONVERSAS
    def create_conversation(self, session_id: str, platform: str, phone_number: str = None, user_id: str = None) -> Optional[str]:
        """Cria nova conversa"""
        if not self.client:
            return None
        
        try:
            conversation_data = {
                'session_id': session_id,
                'platform': platform,
                'phone_number': phone_number,
                'user_id': user_id
            }
            response = self.client.table('conversations').insert(conversation_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao criar conversa: {e}")
            return None
    
    def get_conversation_by_session(self, session_id: str) -> Optional[Dict]:
        """Busca conversa por session_id"""
        if not self.client:
            return None
        
        try:
            response = self.client.table('conversations').select('*').eq('session_id', session_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Erro ao buscar conversa {session_id}: {e}")
            return None
    
    # MENSAGENS
    def save_message(self, conversation_id: str, message_type: str, content: str, metadata: Dict = None) -> Optional[str]:
        """Salva mensagem na conversa"""
        if not self.client:
            return None
        
        try:
            message_data = {
                'conversation_id': conversation_id,
                'message_type': message_type,
                'content': content,
                'metadata': metadata or {}
            }
            response = self.client.table('messages').insert(message_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao salvar mensagem: {e}")
            return None
    
    def get_conversation_messages(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Busca mensagens de uma conversa"""
        if not self.client:
            return []
        
        try:
            response = (self.client.table('messages')
                       .select('*')
                       .eq('conversation_id', conversation_id)
                       .order('created_at', desc=False)
                       .limit(limit)
                       .execute())
            return response.data
        except Exception as e:
            print(f"Erro ao buscar mensagens: {e}")
            return []
    
    # ORÇAMENTOS
    def save_quote(self, conversation_id: str, product_id: str, area: float, coats: int, 
                   labor_included: bool, quote_data: Dict) -> Optional[str]:
        """Salva orçamento"""
        if not self.client:
            return None
        
        try:
            quote_record = {
                'conversation_id': conversation_id,
                'product_id': product_id,
                'area': area,
                'coats': coats,
                'labor_included': labor_included,
                'liters_needed': quote_data.get('liters_needed'),
                'recommended_package': quote_data.get('recommended_package'),
                'costs': quote_data.get('costs'),
                'status': 'draft'
            }
            response = self.client.table('quotes').insert(quote_record).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao salvar orçamento: {e}")
            return None
    
    def get_quotes_by_conversation(self, conversation_id: str) -> List[Dict]:
        """Busca orçamentos de uma conversa"""
        if not self.client:
            return []
        
        try:
            response = (self.client.table('quotes')
                       .select('*, products(*)')
                       .eq('conversation_id', conversation_id)
                       .order('created_at', desc=True)
                       .execute())
            return response.data
        except Exception as e:
            print(f"Erro ao buscar orçamentos: {e}")
            return []
    
    # BASE DE CONHECIMENTO
    def add_knowledge(self, question: str, answer: str, category: str = None, 
                     tags: List[str] = None, source: str = 'manual') -> Optional[str]:
        """Adiciona conhecimento à base"""
        if not self.client:
            return None
        
        try:
            knowledge_data = {
                'question': question,
                'answer': answer,
                'category': category,
                'tags': tags or [],
                'source': source,
                'confidence_score': 1.0
            }
            response = self.client.table('knowledge_base').insert(knowledge_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao adicionar conhecimento: {e}")
            return None
    
    def search_knowledge(self, query: str, category: str = None, limit: int = 10) -> List[Dict]:
        """Busca na base de conhecimento"""
        if not self.client:
            return []
        
        try:
            search_query = self.client.table('knowledge_base').select('*').eq('active', True)
            
            if category:
                search_query = search_query.eq('category', category)
            
            # Busca textual simples (pode ser melhorada com busca semântica)
            search_query = search_query.or_(f'question.ilike.%{query}%,answer.ilike.%{query}%')
            
            response = search_query.limit(limit).execute()
            return response.data
        except Exception as e:
            print(f"Erro ao buscar conhecimento: {e}")
            return []
    
    # FEEDBACK
    def save_feedback(self, conversation_id: str, message_id: str, rating: int, 
                     comment: str = None, feedback_type: str = 'rating') -> Optional[str]:
        """Salva feedback do usuário"""
        if not self.client:
            return None
        
        try:
            feedback_data = {
                'conversation_id': conversation_id,
                'message_id': message_id,
                'rating': rating,
                'comment': comment,
                'feedback_type': feedback_type
            }
            response = self.client.table('feedback').insert(feedback_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao salvar feedback: {e}")
            return None
    
    # CONFIGURAÇÕES
    def get_config(self, key: str) -> Any:
        """Busca configuração do sistema"""
        if not self.client:
            return None
        
        try:
            response = self.client.table('system_config').select('value').eq('key', key).execute()
            if response.data:
                return response.data[0]['value']
            return None
        except Exception as e:
            print(f"Erro ao buscar configuração {key}: {e}")
            return None
    
    def set_config(self, key: str, value: Any, description: str = None) -> bool:
        """Define configuração do sistema"""
        if not self.client:
            return False
        
        try:
            config_data = {
                'key': key,
                'value': value,
                'description': description
            }
            response = (self.client.table('system_config')
                       .upsert(config_data, on_conflict='key')
                       .execute())
            return len(response.data) > 0
        except Exception as e:
            print(f"Erro ao definir configuração {key}: {e}")
            return False
    
    # LOGS
    def log_activity(self, action: str, entity_type: str = None, entity_id: str = None, 
                    details: Dict = None, user_id: str = None, ip_address: str = None) -> Optional[str]:
        """Registra atividade no log"""
        if not self.client:
            return None
        
        try:
            log_data = {
                'action': action,
                'entity_type': entity_type,
                'entity_id': entity_id,
                'details': details or {},
                'user_id': user_id,
                'ip_address': ip_address
            }
            response = self.client.table('activity_logs').insert(log_data).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            print(f"Erro ao registrar log: {e}")
            return None
    
    # ESTATÍSTICAS
    def get_stats(self) -> Dict:
        """Busca estatísticas do sistema"""
        if not self.client:
            return {}
        
        try:
            stats = {}
            
            # Total de produtos ativos
            products_response = self.client.table('products').select('id', count='exact').eq('active', True).execute()
            stats['total_products'] = products_response.count
            
            # Total de conversas
            conversations_response = self.client.table('conversations').select('id', count='exact').execute()
            stats['total_conversations'] = conversations_response.count
            
            # Total de mensagens
            messages_response = self.client.table('messages').select('id', count='exact').execute()
            stats['total_messages'] = messages_response.count
            
            # Total de orçamentos
            quotes_response = self.client.table('quotes').select('id', count='exact').execute()
            stats['total_quotes'] = quotes_response.count
            
            # Feedback médio
            feedback_response = self.client.table('feedback').select('rating').execute()
            if feedback_response.data:
                ratings = [f['rating'] for f in feedback_response.data]
                stats['average_rating'] = sum(ratings) / len(ratings) if ratings else 0
            else:
                stats['average_rating'] = 0
            
            return stats
        except Exception as e:
            print(f"Erro ao buscar estatísticas: {e}")
            return {}
    
    # ==================== MÉTODOS PARA GERENCIAR PROMPTS DE AGENTES ====================
    
    def get_agent_prompts(self, agent_type: str) -> list:
        """Obtém todos os prompts de um agente específico"""
        try:
            if not self.is_connected():
                return []
            
            response = self.client.table('agent_prompts').select('*').eq('agent_type', agent_type).eq('is_active', True).execute()
            return response.data
        
        except Exception as e:
            print(f"Erro ao obter prompts do agente {agent_type}: {e}")
            return []
    
    def get_all_agent_prompts(self) -> list:
        """Obtém todos os prompts de todos os agentes"""
        try:
            if not self.is_connected():
                return []
            
            response = self.client.table('agent_prompts').select('*').eq('is_active', True).execute()
            return response.data
        
        except Exception as e:
            print(f"Erro ao obter todos os prompts: {e}")
            return []
    
    def get_agent_prompt(self, agent_type: str, prompt_type: str) -> dict:
        """Obtém um prompt específico de um agente"""
        try:
            if not self.is_connected():
                return {}
            
            response = self.client.table('agent_prompts').select('*').eq('agent_type', agent_type).eq('prompt_type', prompt_type).eq('is_active', True).single().execute()
            return response.data
        
        except Exception as e:
            print(f"Erro ao obter prompt {agent_type}/{prompt_type}: {e}")
            return {}
    
    def create_agent_prompt(self, agent_type: str, prompt_type: str, prompt_text: str, description: str = None) -> str:
        """Cria um novo prompt para um agente"""
        try:
            if not self.is_connected():
                return None
            
            data = {
                'agent_type': agent_type,
                'prompt_type': prompt_type,
                'prompt_text': prompt_text,
                'description': description,
                'is_active': True
            }
            
            response = self.client.table('agent_prompts').insert(data).execute()
            
            if response.data:
                prompt_id = response.data[0]['id']
                self.log_activity('agent_prompt_created', 'create', None, {
                    'agent_type': agent_type,
                    'prompt_type': prompt_type,
                    'prompt_id': prompt_id
                })
                return prompt_id
            
            return None
        
        except Exception as e:
            print(f"Erro ao criar prompt {agent_type}/{prompt_type}: {e}")
            return None
    
    def update_agent_prompt(self, agent_type: str, prompt_type: str, prompt_text: str, description: str = None) -> bool:
        """Atualiza um prompt existente de um agente"""
        try:
            if not self.is_connected():
                return False
            
            data = {
                'prompt_text': prompt_text
            }
            
            if description is not None:
                data['description'] = description
            
            response = self.client.table('agent_prompts').update(data).eq('agent_type', agent_type).eq('prompt_type', prompt_type).execute()
            
            if response.data:
                self.log_activity('agent_prompt_updated', 'update', None, {
                    'agent_type': agent_type,
                    'prompt_type': prompt_type
                })
                return True
            
            return False
        
        except Exception as e:
            print(f"Erro ao atualizar prompt {agent_type}/{prompt_type}: {e}")
            return False
    
    def delete_agent_prompt(self, agent_type: str, prompt_type: str) -> bool:
        """Remove um prompt de um agente (marca como inativo)"""
        try:
            if not self.is_connected():
                return False
            
            response = self.client.table('agent_prompts').update({'is_active': False}).eq('agent_type', agent_type).eq('prompt_type', prompt_type).execute()
            
            if response.data:
                self.log_activity('agent_prompt_deleted', 'delete', None, {
                    'agent_type': agent_type,
                    'prompt_type': prompt_type
                })
                return True
            
            return False
        
        except Exception as e:
            print(f"Erro ao remover prompt {agent_type}/{prompt_type}: {e}")
            return False

# Instância global do gerenciador Supabase
supabase_manager = SupabaseManager()
