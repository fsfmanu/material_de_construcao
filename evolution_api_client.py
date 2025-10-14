import os
import requests
import json
from typing import Optional, Dict, List, Any
from datetime import datetime

class EvolutionAPIClient:
    def __init__(self):
        # Configurações da Evolution API (definir como variáveis de ambiente)
        self.api_url = os.getenv('EVOLUTION_API_URL', 'http://localhost:8080')
        self.api_key = os.getenv('EVOLUTION_API_KEY', '')
        self.instance_name = os.getenv('EVOLUTION_INSTANCE_NAME', 'agente-tintas')
        
        # Headers padrão para requisições
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }
        
        if not self.api_key:
            print("⚠️  Chave da Evolution API não encontrada. Usando modo local.")
        else:
            print(f"✅ Evolution API configurada: {self.api_url}")
    
    def is_configured(self) -> bool:
        """Verifica se a Evolution API está configurada"""
        return bool(self.api_key and self.api_url)
    
    # GERENCIAMENTO DE INSTÂNCIAS
    def create_instance(self, instance_name: str = None, webhook_url: str = None) -> Dict:
        """Cria uma nova instância do WhatsApp"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        payload = {
            "instanceName": instance_name,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        # Adicionar webhook se fornecido
        if webhook_url:
            payload["webhook"] = {
                "url": webhook_url,
                "events": [
                    "QRCODE_UPDATED",
                    "CONNECTION_UPDATE",
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE",
                    "SEND_MESSAGE"
                ]
            }
        
        try:
            response = requests.post(
                f"{self.api_url}/instance/create",
                headers=self.headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao criar instância: {str(e)}'}
    
    def get_instance_info(self, instance_name: str = None) -> Dict:
        """Busca informações da instância"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        try:
            response = requests.get(
                f"{self.api_url}/instance/fetchInstances",
                headers=self.headers,
                params={'instanceName': instance_name}
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar instância: {str(e)}'}
    
    def get_connection_state(self, instance_name: str = None) -> Dict:
        """Verifica o status da conexão da instância"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        try:
            response = requests.get(
                f"{self.api_url}/instance/connectionState/{instance_name}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao verificar conexão: {str(e)}'}
    
    def delete_instance(self, instance_name: str = None) -> Dict:
        """Remove uma instância"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        try:
            response = requests.delete(
                f"{self.api_url}/instance/delete/{instance_name}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao deletar instância: {str(e)}'}
    
    # WEBHOOK
    def set_webhook(self, webhook_url: str, instance_name: str = None, events: List[str] = None) -> Dict:
        """Configura webhook para a instância"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        if events is None:
            events = [
                "QRCODE_UPDATED",
                "CONNECTION_UPDATE", 
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE"
            ]
        
        payload = {
            "url": webhook_url,
            "webhook_by_events": False,
            "webhook_base64": False,
            "events": events
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/webhook/instance/{instance_name}",
                headers=self.headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao configurar webhook: {str(e)}'}
    
    def get_webhook_info(self, instance_name: str = None) -> Dict:
        """Busca informações do webhook configurado"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        try:
            response = requests.get(
                f"{self.api_url}/webhook/find/{instance_name}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar webhook: {str(e)}'}
    
    # MENSAGENS
    def send_text_message(self, phone_number: str, message: str, instance_name: str = None) -> Dict:
        """Envia mensagem de texto"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        # Formatar número de telefone (remover caracteres especiais)
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.endswith('@s.whatsapp.net'):
            phone_number = f"{phone_number}@s.whatsapp.net"
        
        payload = {
            "number": phone_number,
            "text": message
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/message/sendText/{instance_name}",
                headers=self.headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao enviar mensagem: {str(e)}'}
    
    def send_media_message(self, phone_number: str, media_url: str, caption: str = "", 
                          media_type: str = "image", instance_name: str = None) -> Dict:
        """Envia mensagem com mídia (imagem, documento, etc.)"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        # Formatar número de telefone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.endswith('@s.whatsapp.net'):
            phone_number = f"{phone_number}@s.whatsapp.net"
        
        payload = {
            "number": phone_number,
            "mediaMessage": {
                "media": media_url,
                "caption": caption
            }
        }
        
        endpoint_map = {
            "image": "sendMedia",
            "document": "sendMedia", 
            "audio": "sendWhatsAppAudio",
            "video": "sendMedia"
        }
        
        endpoint = endpoint_map.get(media_type, "sendMedia")
        
        try:
            response = requests.post(
                f"{self.api_url}/message/{endpoint}/{instance_name}",
                headers=self.headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao enviar mídia: {str(e)}'}
    
    def send_button_message(self, phone_number: str, text: str, buttons: List[Dict], 
                           footer: str = "", instance_name: str = None) -> Dict:
        """Envia mensagem com botões"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        # Formatar número de telefone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.endswith('@s.whatsapp.net'):
            phone_number = f"{phone_number}@s.whatsapp.net"
        
        payload = {
            "number": phone_number,
            "buttonMessage": {
                "text": text,
                "footer": footer,
                "buttons": buttons
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/message/sendButtons/{instance_name}",
                headers=self.headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao enviar botões: {str(e)}'}
    
    def send_list_message(self, phone_number: str, text: str, button_text: str, 
                         sections: List[Dict], footer: str = "", instance_name: str = None) -> Dict:
        """Envia mensagem com lista de opções"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        # Formatar número de telefone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.endswith('@s.whatsapp.net'):
            phone_number = f"{phone_number}@s.whatsapp.net"
        
        payload = {
            "number": phone_number,
            "listMessage": {
                "text": text,
                "buttonText": button_text,
                "footer": footer,
                "sections": sections
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/message/sendList/{instance_name}",
                headers=self.headers,
                json=payload
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao enviar lista: {str(e)}'}
    
    # CONTATOS E CHATS
    def get_contacts(self, instance_name: str = None) -> Dict:
        """Busca lista de contatos"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        try:
            response = requests.get(
                f"{self.api_url}/chat/findContacts/{instance_name}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar contatos: {str(e)}'}
    
    def get_chats(self, instance_name: str = None) -> Dict:
        """Busca lista de chats"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        try:
            response = requests.get(
                f"{self.api_url}/chat/findChats/{instance_name}",
                headers=self.headers
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar chats: {str(e)}'}
    
    def get_chat_messages(self, phone_number: str, limit: int = 20, instance_name: str = None) -> Dict:
        """Busca mensagens de um chat específico"""
        if not self.is_configured():
            return {'error': 'Evolution API não configurada'}
        
        instance_name = instance_name or self.instance_name
        
        # Formatar número de telefone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if not phone_number.endswith('@s.whatsapp.net'):
            phone_number = f"{phone_number}@s.whatsapp.net"
        
        try:
            response = requests.get(
                f"{self.api_url}/chat/findMessages/{instance_name}",
                headers=self.headers,
                params={
                    'number': phone_number,
                    'limit': limit
                }
            )
            return response.json()
        except Exception as e:
            return {'error': f'Erro ao buscar mensagens: {str(e)}'}
    
    # UTILITÁRIOS
    def format_phone_number(self, phone: str) -> str:
        """Formata número de telefone para o padrão do WhatsApp"""
        # Remove todos os caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))
        
        # Adiciona código do país se não tiver (assume Brasil +55)
        if len(phone) == 11 and phone.startswith('11'):
            phone = '55' + phone
        elif len(phone) == 10:
            phone = '5511' + phone
        elif len(phone) == 9:
            phone = '55119' + phone
        
        return f"{phone}@s.whatsapp.net"
    
    def create_button(self, button_id: str, display_text: str) -> Dict:
        """Cria um botão para mensagens interativas"""
        return {
            "buttonId": button_id,
            "buttonText": {
                "displayText": display_text
            },
            "type": 1
        }
    
    def create_list_section(self, title: str, rows: List[Dict]) -> Dict:
        """Cria uma seção para mensagens de lista"""
        return {
            "title": title,
            "rows": rows
        }
    
    def create_list_row(self, row_id: str, title: str, description: str = "") -> Dict:
        """Cria uma linha para seções de lista"""
        return {
            "rowId": row_id,
            "title": title,
            "description": description
        }
    
    # WEBHOOK HANDLERS
    def process_webhook_message(self, webhook_data: Dict) -> Dict:
        """Processa dados recebidos via webhook"""
        try:
            event_type = webhook_data.get('event')
            instance_name = webhook_data.get('instance')
            data = webhook_data.get('data', {})
            
            result = {
                'event_type': event_type,
                'instance_name': instance_name,
                'processed_at': datetime.now().isoformat()
            }
            
            if event_type == 'MESSAGES_UPSERT':
                # Processar mensagem recebida
                message = data.get('message', {})
                key = message.get('key', {})
                
                result.update({
                    'message_id': key.get('id'),
                    'from_me': key.get('fromMe', False),
                    'phone_number': key.get('remoteJid', '').replace('@s.whatsapp.net', ''),
                    'message_type': message.get('messageType'),
                    'message_content': self._extract_message_content(message),
                    'timestamp': message.get('messageTimestamp')
                })
                
            elif event_type == 'CONNECTION_UPDATE':
                # Processar atualização de conexão
                result.update({
                    'connection_state': data.get('state'),
                    'qr_code': data.get('qrcode')
                })
                
            elif event_type == 'QRCODE_UPDATED':
                # Processar atualização do QR Code
                result.update({
                    'qr_code': data.get('qrcode')
                })
            
            return result
            
        except Exception as e:
            return {'error': f'Erro ao processar webhook: {str(e)}'}
    
    def _extract_message_content(self, message: Dict) -> str:
        """Extrai o conteúdo da mensagem baseado no tipo"""
        message_type = message.get('messageType', '')
        
        if message_type == 'conversation':
            return message.get('message', {}).get('conversation', '')
        elif message_type == 'extendedTextMessage':
            return message.get('message', {}).get('extendedTextMessage', {}).get('text', '')
        elif message_type == 'imageMessage':
            return message.get('message', {}).get('imageMessage', {}).get('caption', '[Imagem]')
        elif message_type == 'documentMessage':
            return message.get('message', {}).get('documentMessage', {}).get('caption', '[Documento]')
        elif message_type == 'audioMessage':
            return '[Áudio]'
        elif message_type == 'videoMessage':
            return message.get('message', {}).get('videoMessage', {}).get('caption', '[Vídeo]')
        else:
            return f'[{message_type}]'

# Instância global do cliente Evolution API
evolution_client = EvolutionAPIClient()
