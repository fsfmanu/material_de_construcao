import json
import uuid
from typing import Dict, List, Optional
from datetime import datetime

from evolution_api_client import evolution_client
from supabase_client import supabase_manager
from semantic_search_system import SemanticSearchSystem

class WhatsAppService:
    def __init__(self):
        self.evolution_client = evolution_client
        self.supabase = supabase_manager
        self.semantic_search = SemanticSearchSystem('/home/ubuntu/structured_knowledge_refined.json')
        
        # Configurações do agente
        self.agent_name = "Especialista em Tintas"
        self.greeting_message = "Olá! 👋 Sou seu especialista em tintas. Como posso ajudá-lo hoje?"
        
        # Estados de conversa
        self.conversation_states = {}
        
    def process_incoming_message(self, webhook_data: Dict) -> Dict:
        """Processa mensagem recebida via webhook da Evolution API"""
        try:
            # Processar dados do webhook
            processed = self.evolution_client.process_webhook_message(webhook_data)
            
            if processed.get('error'):
                return processed
            
            event_type = processed.get('event_type')
            
            if event_type == 'MESSAGES_UPSERT':
                return self._handle_message_received(processed)
            elif event_type == 'CONNECTION_UPDATE':
                return self._handle_connection_update(processed)
            elif event_type == 'QRCODE_UPDATED':
                return self._handle_qrcode_update(processed)
            else:
                return {'status': 'ignored', 'event_type': event_type}
                
        except Exception as e:
            return {'error': f'Erro ao processar mensagem: {str(e)}'}
    
    def _handle_message_received(self, message_data: Dict) -> Dict:
        """Processa mensagem recebida do usuário"""
        try:
            # Extrair dados da mensagem
            phone_number = message_data.get('phone_number', '')
            message_content = message_data.get('message_content', '')
            from_me = message_data.get('from_me', False)
            
            # Ignorar mensagens enviadas pelo próprio bot
            if from_me:
                return {'status': 'ignored', 'reason': 'message_from_bot'}
            
            # Ignorar mensagens vazias ou de sistema
            if not message_content or message_content.startswith('['):
                return {'status': 'ignored', 'reason': 'empty_or_system_message'}
            
            # Buscar ou criar conversa
            conversation = self._get_or_create_conversation(phone_number)
            
            # Salvar mensagem do usuário
            self.supabase.save_message(
                conversation['id'], 
                'user', 
                message_content,
                {'phone_number': phone_number, 'whatsapp_data': message_data}
            )
            
            # Gerar resposta do agente
            response = self._generate_agent_response(message_content, conversation['id'], phone_number)
            
            # Enviar resposta via WhatsApp
            if response.get('message'):
                send_result = self.send_message(phone_number, response['message'])
                
                # Salvar resposta do agente
                self.supabase.save_message(
                    conversation['id'],
                    'agent',
                    response['message'],
                    {
                        'search_results': response.get('search_results', []),
                        'products_found': response.get('products_found', []),
                        'send_result': send_result
                    }
                )
                
                return {
                    'status': 'processed',
                    'conversation_id': conversation['id'],
                    'response_sent': True,
                    'send_result': send_result
                }
            
            return {
                'status': 'processed',
                'conversation_id': conversation['id'],
                'response_sent': False
            }
            
        except Exception as e:
            return {'error': f'Erro ao processar mensagem recebida: {str(e)}'}
    
    def _handle_connection_update(self, connection_data: Dict) -> Dict:
        """Processa atualização de status de conexão"""
        state = connection_data.get('connection_state')
        
        # Log da atividade
        self.supabase.log_activity(
            'whatsapp_connection_update',
            'connection',
            connection_data.get('instance_name'),
            {'state': state, 'timestamp': datetime.now().isoformat()}
        )
        
        return {'status': 'logged', 'connection_state': state}
    
    def _handle_qrcode_update(self, qrcode_data: Dict) -> Dict:
        """Processa atualização do QR Code"""
        qr_code = qrcode_data.get('qr_code')
        
        # Log da atividade
        self.supabase.log_activity(
            'whatsapp_qrcode_update',
            'qrcode',
            qrcode_data.get('instance_name'),
            {'has_qrcode': bool(qr_code), 'timestamp': datetime.now().isoformat()}
        )
        
        return {'status': 'logged', 'qr_code_available': bool(qr_code)}
    
    def _get_or_create_conversation(self, phone_number: str) -> Dict:
        """Busca conversa existente ou cria uma nova"""
        # Gerar session_id baseado no número de telefone
        session_id = f"whatsapp_{phone_number}"
        
        # Buscar conversa existente
        conversation = self.supabase.get_conversation_by_session(session_id)
        
        if not conversation:
            # Criar nova conversa
            conversation_id = self.supabase.create_conversation(
                session_id=session_id,
                platform='whatsapp',
                phone_number=phone_number
            )
            
            if conversation_id:
                conversation = {
                    'id': conversation_id,
                    'session_id': session_id,
                    'platform': 'whatsapp',
                    'phone_number': phone_number
                }
                
                # Enviar mensagem de boas-vindas
                self.send_message(phone_number, self.greeting_message)
                
                # Salvar mensagem de boas-vindas
                self.supabase.save_message(
                    conversation_id,
                    'agent',
                    self.greeting_message,
                    {'type': 'greeting'}
                )
        
        return conversation
    
    def _generate_agent_response(self, user_message: str, conversation_id: str, phone_number: str) -> Dict:
        """Gera resposta do agente baseada na mensagem do usuário"""
        try:
            # Verificar se é uma saudação
            greetings = ['oi', 'olá', 'ola', 'bom dia', 'boa tarde', 'boa noite', 'hey', 'e aí']
            if any(greeting in user_message.lower() for greeting in greetings):
                return {
                    'message': f"Olá! 👋 Sou seu {self.agent_name}. Posso ajudá-lo com:\n\n🎨 Recomendações de tintas\n📏 Cálculo de quantidade\n💰 Orçamentos\n🔧 Dicas técnicas\n\nO que você precisa hoje?",
                    'search_results': [],
                    'products_found': []
                }
            
            # Verificar se é uma solicitação de orçamento
            if any(word in user_message.lower() for word in ['orçamento', 'orcamento', 'preço', 'preco', 'quanto custa', 'valor']):
                return self._handle_quote_request(user_message, conversation_id, phone_number)
            
            # Verificar se é uma pergunta sobre cálculo
            if any(word in user_message.lower() for word in ['calcular', 'quantidade', 'litros', 'metros', 'área', 'area']):
                return self._handle_calculation_request(user_message)
            
            # Busca semântica na base de conhecimento
            search_results = self.semantic_search.search(user_message, top_k=3)
            
            if search_results:
                # Encontrou produtos/informações relevantes
                response_parts = [f"Encontrei algumas informações que podem ajudar:\n"]
                
                products_found = []
                for i, result in enumerate(search_results[:2], 1):
                    product_info = result.get('metadata', {})
                    score = result.get('score', 0)
                    
                    if score > 0.5:  # Apenas resultados com boa relevância
                        products_found.append(product_info)
                        
                        response_parts.append(f"🎨 **{product_info.get('name', 'Produto')}**")
                        if product_info.get('brand'):
                            response_parts.append(f"Marca: {product_info.get('brand')}")
                        if product_info.get('description'):
                            response_parts.append(f"{product_info.get('description')}")
                        if product_info.get('coverage'):
                            response_parts.append(f"Rendimento: {product_info.get('coverage')}")
                        response_parts.append("")
                
                if products_found:
                    response_parts.append("💬 Gostaria de mais detalhes sobre algum produto ou precisa de um orçamento?")
                    
                    return {
                        'message': '\n'.join(response_parts),
                        'search_results': search_results,
                        'products_found': products_found
                    }
            
            # Resposta padrão quando não encontra informações específicas
            return {
                'message': f"Entendi sua pergunta sobre tintas. Posso ajudá-lo de várias formas:\n\n🔍 **Buscar produtos específicos** - Me diga que tipo de tinta precisa\n📏 **Calcular quantidade** - Informe as dimensões do ambiente\n💰 **Fazer orçamento** - Preciso saber a área e o tipo de tinta\n❓ **Tirar dúvidas técnicas** - Sobre aplicação, cores, etc.\n\nO que você gostaria de fazer?",
                'search_results': [],
                'products_found': []
            }
            
        except Exception as e:
            return {
                'message': "Desculpe, tive um problema técnico. Pode repetir sua pergunta?",
                'error': str(e),
                'search_results': [],
                'products_found': []
            }
    
    def _handle_quote_request(self, user_message: str, conversation_id: str, phone_number: str) -> Dict:
        """Processa solicitação de orçamento"""
        # Buscar produtos mencionados na mensagem
        search_results = self.semantic_search.search(user_message, top_k=2)
        
        if search_results and search_results[0].get('score', 0) > 0.6:
            product = search_results[0].get('metadata', {})
            
            # Criar botões para facilitar a interação
            buttons_message = f"Encontrei este produto para seu orçamento:\n\n🎨 **{product.get('name', 'Produto')}**\n"
            if product.get('brand'):
                buttons_message += f"Marca: {product.get('brand')}\n"
            if product.get('coverage'):
                buttons_message += f"Rendimento: {product.get('coverage')}\n\n"
            
            buttons_message += "Para fazer o orçamento, preciso saber a área a ser pintada. Você pode me informar:\n\n📐 As dimensões (largura x altura)\n📏 A área total em m²\n\nOu se preferir, posso te ajudar a calcular!"
            
            return {
                'message': buttons_message,
                'search_results': search_results,
                'products_found': [product]
            }
        else:
            return {
                'message': "Para fazer um orçamento preciso, me informe:\n\n🎨 **Tipo de tinta** (ex: acrílica, esmalte, etc.)\n📍 **Local de aplicação** (quarto, sala, externa, etc.)\n📏 **Área a ser pintada** (em m² ou dimensões)\n\nCom essas informações posso te dar um orçamento detalhado!",
                'search_results': [],
                'products_found': []
            }
    
    def _handle_calculation_request(self, user_message: str) -> Dict:
        """Processa solicitação de cálculo de quantidade"""
        return {
            'message': "Vou te ajudar a calcular a quantidade de tinta! 📏\n\nPreciso das seguintes informações:\n\n📐 **Dimensões do ambiente:**\n• Largura (metros)\n• Altura (metros)\n• Número de paredes\n\n🚪 **Vãos (portas e janelas):**\n• Área total dos vãos em m²\n\n🎨 **Tipo de tinta:**\n• Qual tinta pretende usar?\n\nMe informe esses dados e calcularei exatamente quantos litros você precisará!",
            'search_results': [],
            'products_found': []
        }
    
    def send_message(self, phone_number: str, message: str) -> Dict:
        """Envia mensagem via WhatsApp"""
        try:
            result = self.evolution_client.send_text_message(phone_number, message)
            
            # Log da atividade
            self.supabase.log_activity(
                'whatsapp_message_sent',
                'message',
                None,
                {
                    'phone_number': phone_number,
                    'message_length': len(message),
                    'success': not result.get('error'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return result
            
        except Exception as e:
            return {'error': f'Erro ao enviar mensagem: {str(e)}'}
    
    def send_button_message(self, phone_number: str, text: str, buttons: List[Dict], footer: str = "") -> Dict:
        """Envia mensagem com botões"""
        try:
            result = self.evolution_client.send_button_message(phone_number, text, buttons, footer)
            
            # Log da atividade
            self.supabase.log_activity(
                'whatsapp_button_message_sent',
                'message',
                None,
                {
                    'phone_number': phone_number,
                    'buttons_count': len(buttons),
                    'success': not result.get('error'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return result
            
        except Exception as e:
            return {'error': f'Erro ao enviar mensagem com botões: {str(e)}'}
    
    def send_product_catalog(self, phone_number: str, products: List[Dict]) -> Dict:
        """Envia catálogo de produtos formatado"""
        try:
            if not products:
                return self.send_message(phone_number, "Não encontrei produtos para mostrar no momento.")
            
            catalog_message = "🎨 **Catálogo de Tintas**\n\n"
            
            for i, product in enumerate(products[:5], 1):  # Máximo 5 produtos
                catalog_message += f"**{i}. {product.get('name', 'Produto')}**\n"
                if product.get('brand'):
                    catalog_message += f"Marca: {product.get('brand')}\n"
                if product.get('description'):
                    catalog_message += f"{product.get('description')[:100]}...\n"
                if product.get('coverage'):
                    catalog_message += f"Rendimento: {product.get('coverage')}\n"
                catalog_message += "\n"
            
            catalog_message += "💬 Digite o número do produto para mais detalhes ou solicite um orçamento!"
            
            return self.send_message(phone_number, catalog_message)
            
        except Exception as e:
            return {'error': f'Erro ao enviar catálogo: {str(e)}'}
    
    def get_conversation_history(self, phone_number: str, limit: int = 10) -> List[Dict]:
        """Busca histórico de conversa"""
        try:
            session_id = f"whatsapp_{phone_number}"
            conversation = self.supabase.get_conversation_by_session(session_id)
            
            if conversation:
                return self.supabase.get_conversation_messages(conversation['id'], limit)
            
            return []
            
        except Exception as e:
            print(f"Erro ao buscar histórico: {e}")
            return []
    
    def get_whatsapp_stats(self) -> Dict:
        """Busca estatísticas do WhatsApp"""
        try:
            stats = self.supabase.get_stats()
            
            # Adicionar estatísticas específicas do WhatsApp
            whatsapp_conversations = 0
            whatsapp_messages = 0
            
            # Aqui você pode adicionar queries específicas para contar conversas e mensagens do WhatsApp
            
            stats.update({
                'whatsapp_conversations': whatsapp_conversations,
                'whatsapp_messages': whatsapp_messages,
                'evolution_api_configured': self.evolution_client.is_configured()
            })
            
            return stats
            
        except Exception as e:
            return {'error': f'Erro ao buscar estatísticas: {str(e)}'}

# Instância global do serviço WhatsApp
whatsapp_service = WhatsAppService()
