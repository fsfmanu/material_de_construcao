from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime
from dataclasses import asdict

# Adicionar o diretório pai ao path para importar o sistema de busca semântica
sys.path.append('/home/ubuntu')
from semantic_search_system import SemanticSearchSystem
from product_manager import product_manager
from supabase_client import supabase_manager
from evolution_api_client import evolution_client
from whatsapp_service import whatsapp_service
from prompt_manager import prompt_manager
from pisos_agent import pisos_agent
from pisos_semantic_search import pisos_search_system
from orchestrator_agent import orchestrator_agent
from reviewer_agent import reviewer_agent
from pdf_upload_processor import pdf_processor
from knowledge_editor import knowledge_editor
from version_manager import version_manager

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend React

# Inicializar sistemas
print("Inicializando sistemas...")
search_system = SemanticSearchSystem('/home/ubuntu/structured_knowledge_refined.json')
prompt_manager.load_prompts_cache()  # Carregar prompts do Supabase
print(f"✅ Sistema de busca semântica (Tintas) inicializado com {len(search_system.knowledge_base)} itens")
print(f"✅ Sistema de busca semântica (Pisos) inicializado com {len(pisos_search_system.knowledge_base)} itens")
print(f"✅ Agente de Pisos inicializado - Especialidades: {len(pisos_agent.expertise_areas)}")
print(f"✅ Agente Orquestrador inicializado - OpenAI: {'Disponível' if orchestrator_agent._is_openai_available() else 'Indisponível'}")
print(f"✅ Agente Revisor inicializado - OpenAI: {'Disponível' if reviewer_agent._is_openai_available() else 'Indisponível'}")
print(f"✅ Gerenciador de produtos inicializado com {len(product_manager.get_all_products())} produtos")
print(f"✅ Gerenciador de prompts inicializado com {len(prompt_manager.get_all_prompts())} prompts")
print(f"✅ Supabase: {'Conectado' if supabase_manager.is_connected() else 'Modo local'}")
print(f"✅ Evolution API: {'Configurada' if evolution_client.is_configured() else 'Não configurada'}")
print(f"✅ WhatsApp Service: Inicializado")

# ==================== ENDPOINTS EXISTENTES ====================

@app.route('/api/search', methods=['POST'])
def semantic_search():
    """Endpoint para busca semântica"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        similarity_threshold = data.get('similarity_threshold', 0.3)
        
        if not query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        results = search_system.search(query, top_k=top_k, similarity_threshold=similarity_threshold)
        
        # Log da busca no Supabase
        supabase_manager.log_activity(
            'semantic_search',
            'search',
            None,
            {'query': query, 'results_count': len(results)}
        )
        
        return jsonify({
            'query': query,
            'results': results,
            'total_results': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Endpoint para recomendações de produtos"""
    try:
        data = request.get_json()
        requirements = data.get('requirements', {})
        
        if not requirements:
            return jsonify({'error': 'Requisitos são obrigatórios'}), 400
        
        recommendations = search_system.get_product_recommendations(requirements)
        
        # Log da recomendação no Supabase
        supabase_manager.log_activity(
            'product_recommendation',
            'recommendation',
            None,
            {'requirements': requirements, 'recommendations_count': len(recommendations)}
        )
        
        return jsonify({
            'requirements': requirements,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_agent():
    """Endpoint para chat com o agente especialista"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', f"web_{datetime.now().timestamp()}")
        
        if not message:
            return jsonify({'error': 'Mensagem é obrigatória'}), 400
        
        # Buscar ou criar conversa
        conversation = supabase_manager.get_conversation_by_session(session_id)
        if not conversation:
            conversation_id = supabase_manager.create_conversation(
                session_id=session_id,
                platform='web'
            )
            conversation = {'id': conversation_id, 'session_id': session_id}
        
        # Salvar mensagem do usuário
        supabase_manager.save_message(
            conversation['id'],
            'user',
            message,
            {'platform': 'web'}
        )
        
        # Buscar informações relevantes na base de conhecimento
        search_results = search_system.search(message, top_k=3, similarity_threshold=0.2)
        
        # Gerar resposta baseada nos resultados da busca
        response = generate_agent_response(message, search_results)
        
        # Salvar resposta do agente
        supabase_manager.save_message(
            conversation['id'],
            'agent',
            response,
            {'search_results': search_results, 'platform': 'web'}
        )
        
        return jsonify({
            'user_message': message,
            'agent_response': response,
            'search_results': search_results,
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_agent_response(user_message, search_results):
    """Gera resposta do agente baseada nos resultados da busca semântica"""
    message_lower = user_message.lower()
    
    # Usar prompt do gerenciador de prompts
    greeting = prompt_manager.get_prompt('tintas', 'initial_greeting')
    response = greeting + " "
    
    if search_results:
        # Usar prompt para introdução de recomendações
        intro = prompt_manager.get_prompt('tintas', 'product_recommendation_intro', count=len(search_results))
        response += intro + "\n\n"
        
        for i, result in enumerate(search_results, 1):
            doc = result['document']
            score = result['similarity_score']
            
            response += f"**{i}. {doc.get('product_name', 'Produto')}** da marca **{doc.get('brand', 'Marca')}**\n"
            response += f"- Tipo: {doc.get('type', 'N/A')}\n"
            
            if doc.get('coverage'):
                response += f"- Rendimento: {doc.get('coverage')}\n"
            
            if doc.get('features'):
                features = doc.get('features', [])[:3]  # Primeiras 3 características
                response += f"- Características: {', '.join(features)}\n"
            
            if doc.get('use_case'):
                use_cases = doc.get('use_case', [])[:3]  # Primeiros 3 casos de uso
                response += f"- Indicado para: {', '.join(use_cases)}\n"
            
            response += f"- Relevância: {score:.1%}\n\n"
    
    # Adicionar orientações específicas baseadas na consulta
    if 'orçamento' in message_lower or 'preço' in message_lower or 'custo' in message_lower:
        budget_prompt = prompt_manager.get_prompt('tintas', 'budget_request')
        response += "\n" + budget_prompt
    
    elif 'descasca' in message_lower or 'problema' in message_lower:
        diagnosis_prompt = prompt_manager.get_prompt('tintas', 'paint_problem_diagnosis')
        response += "\n" + diagnosis_prompt
    
    elif 'calcul' in message_lower or 'quantidade' in message_lower:
        calculation_prompt = prompt_manager.get_prompt('tintas', 'calculation_help')
        response += "\n" + calculation_prompt
    
    elif not search_results:
        no_results_prompt = prompt_manager.get_prompt('tintas', 'no_results_found')
        response += no_results_prompt
    
    return response

@app.route('/api/calculate-paint', methods=['POST'])
def calculate_paint():
    """Endpoint para cálculo de quantidade de tinta"""
    try:
        data = request.get_json()
        
        width = float(data.get('width', 0))
        height = float(data.get('height', 0))
        walls = int(data.get('walls', 0))
        openings = float(data.get('openings', 0))
        coverage = float(data.get('coverage', 12))  # m²/L
        coats = int(data.get('coats', 2))
        
        if width <= 0 or height <= 0 or walls <= 0:
            return jsonify({'error': 'Dimensões devem ser maiores que zero'}), 400
        
        # Calcular área total
        total_area = (width * height * walls) - openings
        
        # Calcular quantidade de tinta (com 10% de margem)
        liters_needed = (total_area / coverage / coats) * 1.1
        liters_needed = round(liters_needed, 1)
        
        # Sugerir embalagens
        if liters_needed <= 3.6:
            suggested_package = "1 Galão de 3,6L"
        elif liters_needed <= 18:
            suggested_package = "1 Lata de 18L"
        else:
            packages = int(liters_needed / 18) + (1 if liters_needed % 18 > 0 else 0)
            suggested_package = f"{packages} Lata(s) de 18L"
        
        # Log do cálculo no Supabase
        supabase_manager.log_activity(
            'paint_calculation',
            'calculation',
            None,
            {
                'area': total_area,
                'liters_needed': liters_needed,
                'calculation_params': data
            }
        )
        
        return jsonify({
            'total_area': round(total_area, 1),
            'liters_needed': liters_needed,
            'suggested_package': suggested_package,
            'calculation_details': {
                'width': width,
                'height': height,
                'walls': walls,
                'openings': openings,
                'coverage': coverage,
                'coats': coats
            }
        })
    
    except ValueError:
        return jsonify({'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS DE PRODUTOS ====================

@app.route('/api/products', methods=['GET'])
def get_all_products():
    """Endpoint para listar todos os produtos do catálogo comercial"""
    try:
        # Buscar produtos do Supabase se conectado, senão usar local
        if supabase_manager.is_connected():
            products = supabase_manager.get_all_products()
        else:
            products = product_manager.get_all_products()
        
        return jsonify({
            'products': products,
            'total_products': len(products)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Endpoint para obter produto específico"""
    try:
        if supabase_manager.is_connected():
            product = supabase_manager.get_product_by_id(product_id)
        else:
            product = product_manager.get_product_by_id(product_id)
        
        if product:
            return jsonify({'product': product})
        else:
            return jsonify({'error': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products', methods=['POST'])
def add_product():
    """Endpoint para adicionar novo produto"""
    try:
        data = request.get_json()
        
        if supabase_manager.is_connected():
            product_id = supabase_manager.create_product(data)
        else:
            product_id = product_manager.add_product(data)
        
        return jsonify({'message': 'Produto adicionado com sucesso', 'product_id': product_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    """Endpoint para atualizar produto"""
    try:
        data = request.get_json()
        
        if supabase_manager.is_connected():
            success = supabase_manager.update_product(product_id, data)
        else:
            success = product_manager.update_product(product_id, data)
        
        if success:
            return jsonify({'message': 'Produto atualizado com sucesso'})
        else:
            return jsonify({'error': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Endpoint para remover produto"""
    try:
        if supabase_manager.is_connected():
            success = supabase_manager.delete_product(product_id)
        else:
            success = product_manager.delete_product(product_id)
        
        if success:
            return jsonify({'message': 'Produto removido com sucesso'})
        else:
            return jsonify({'error': 'Produto não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/quote', methods=['POST'])
def generate_quote():
    """Endpoint para gerar orçamento"""
    try:
        data = request.get_json()
        area = float(data.get('area', 0))
        product_id = data.get('product_id', '')
        coats = int(data.get('coats', 2))
        labor_included = data.get('labor_included', False)
        session_id = data.get('session_id')
        
        if area <= 0:
            return jsonify({'error': 'Área deve ser maior que zero'}), 400
        
        if not product_id:
            return jsonify({'error': 'ID do produto é obrigatório'}), 400
        
        # Gerar orçamento
        if supabase_manager.is_connected():
            # Buscar produto no Supabase
            product = supabase_manager.get_product_by_id(product_id)
            if not product:
                return jsonify({'error': 'Produto não encontrado'}), 404
            
            # Calcular orçamento
            quote = calculate_quote_from_product(area, product, coats, labor_included)
            
            # Salvar orçamento no Supabase
            if session_id:
                conversation = supabase_manager.get_conversation_by_session(session_id)
                if conversation:
                    supabase_manager.create_quote(
                        conversation['id'],
                        product_id,
                        area,
                        coats,
                        labor_included,
                        quote
                    )
        else:
            quote = product_manager.calculate_quote(area, product_id, coats, labor_included)
        
        if quote:
            return jsonify({'quote': quote})
        else:
            return jsonify({'error': 'Produto não encontrado ou sem embalagens disponíveis'}), 404
    
    except ValueError:
        return jsonify({'error': 'Valores numéricos inválidos'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def calculate_quote_from_product(area, product, coats, labor_included):
    """Calcula orçamento baseado no produto do Supabase"""
    try:
        # Extrair informações do produto
        coverage = float(product.get('coverage', '12').split()[0])  # Assumir primeiro número
        packages = product.get('packages', [])
        
        if not packages:
            return None
        
        # Calcular quantidade necessária
        liters_needed = (area / coverage) * coats * 1.1  # 10% margem
        
        # Encontrar melhor embalagem
        best_package = None
        best_cost = float('inf')
        
        for package in packages:
            size = package.get('size', 0)
            price = package.get('price', 0)
            
            if size > 0 and price > 0:
                packages_needed = int(liters_needed / size) + (1 if liters_needed % size > 0 else 0)
                total_cost = packages_needed * price
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_package = {
                        'size': size,
                        'price': price,
                        'quantity': packages_needed,
                        'total_liters': packages_needed * size,
                        'total_cost': total_cost
                    }
        
        if not best_package:
            return None
        
        # Calcular custos adicionais
        labor_cost = area * 15.0 if labor_included else 0  # R$ 15/m²
        total_cost = best_package['total_cost'] + labor_cost
        
        return {
            'area': area,
            'coats': coats,
            'liters_needed': round(liters_needed, 1),
            'recommended_package': best_package,
            'labor_cost': labor_cost,
            'total_cost': total_cost,
            'product': {
                'id': product.get('product_id'),
                'name': product.get('name'),
                'brand': product.get('brand')
            }
        }
        
    except Exception as e:
        print(f"Erro ao calcular orçamento: {e}")
        return None

# ==================== ENDPOINTS DO WHATSAPP ====================

@app.route('/webhook/evolution', methods=['POST'])
def evolution_webhook():
    """Webhook para receber eventos da Evolution API"""
    try:
        webhook_data = request.get_json()
        
        # Processar mensagem via WhatsApp Service
        result = whatsapp_service.process_incoming_message(webhook_data)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/whatsapp/send', methods=['POST'])
def send_whatsapp_message():
    """Endpoint para enviar mensagem via WhatsApp"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number', '')
        message = data.get('message', '')
        
        if not phone_number or not message:
            return jsonify({'error': 'Número e mensagem são obrigatórios'}), 400
        
        result = whatsapp_service.send_message(phone_number, message)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/whatsapp/instance/status', methods=['GET'])
def get_whatsapp_status():
    """Endpoint para verificar status da instância WhatsApp"""
    try:
        status = evolution_client.get_connection_state()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/whatsapp/instance/create', methods=['POST'])
def create_whatsapp_instance():
    """Endpoint para criar instância WhatsApp"""
    try:
        data = request.get_json()
        instance_name = data.get('instance_name', evolution_client.instance_name)
        webhook_url = data.get('webhook_url')
        
        result = evolution_client.create_instance(instance_name, webhook_url)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS DE ESTATÍSTICAS ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Endpoint para obter estatísticas do sistema"""
    try:
        if supabase_manager.is_connected():
            stats = supabase_manager.get_stats()
        else:
            stats = {
                'total_products': len(product_manager.get_all_products()),
                'total_conversations': 0,
                'total_messages': 0,
                'total_quotes': 0,
                'mode': 'local'
            }
        
        # Adicionar estatísticas do WhatsApp
        whatsapp_stats = whatsapp_service.get_whatsapp_stats()
        stats.update(whatsapp_stats)
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Endpoint para listar conversas"""
    try:
        if supabase_manager.is_connected():
            conversations = supabase_manager.get_recent_conversations(limit=50)
            return jsonify({'conversations': conversations})
        else:
            return jsonify({'conversations': [], 'message': 'Supabase não conectado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    """Endpoint para obter mensagens de uma conversa"""
    try:
        if supabase_manager.is_connected():
            messages = supabase_manager.get_conversation_messages(conversation_id)
            return jsonify({'messages': messages})
        else:
            return jsonify({'messages': [], 'message': 'Supabase não conectado'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS DE CONFIGURAÇÃO ====================

@app.route('/api/config', methods=['GET'])
def get_config():
    """Endpoint para obter configurações do sistema"""
    try:
        if supabase_manager.is_connected():
            config = supabase_manager.get_system_config()
        else:
            config = {}
        
        # Adicionar status dos serviços
        config.update({
            'services': {
                'supabase': supabase_manager.is_connected(),
                'evolution_api': evolution_client.is_configured(),
                'semantic_search': len(search_system.knowledge_base) > 0,
                'product_manager': len(product_manager.get_all_products()) > 0
            }
        })
        
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Endpoint para atualizar configurações do sistema"""
    try:
        data = request.get_json()
        
        if supabase_manager.is_connected():
            for key, value in data.items():
                supabase_manager.set_system_config(key, value)
            return jsonify({'message': 'Configurações atualizadas com sucesso'})
        else:
            return jsonify({'error': 'Supabase não conectado'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS LEGADOS ====================

@app.route('/api/catalog/export', methods=['GET'])
def export_catalog():
    """Endpoint para exportar catálogo completo"""
    try:
        if supabase_manager.is_connected():
            products = supabase_manager.get_all_products()
            catalog = {'products': products, 'exported_at': datetime.now().isoformat()}
        else:
            catalog = product_manager.export_catalog()
        
        return jsonify(catalog)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/catalog/import', methods=['POST'])
def import_catalog():
    """Endpoint para importar catálogo"""
    try:
        data = request.get_json()
        
        if supabase_manager.is_connected():
            # Importar para Supabase
            products = data.get('products', [])
            success_count = 0
            
            for product in products:
                try:
                    supabase_manager.create_product(product)
                    success_count += 1
                except Exception as e:
                    print(f"Erro ao importar produto {product.get('name', 'N/A')}: {e}")
            
            return jsonify({
                'message': f'Catálogo importado com sucesso',
                'imported_products': success_count,
                'total_products': len(products)
            })
        else:
            success = product_manager.import_catalog(data)
            if success:
                return jsonify({'message': 'Catálogo importado com sucesso'})
            else:
                return jsonify({'error': 'Formato de catálogo inválido'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PARA GERENCIAMENTO DE PROMPTS ====================

@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Obtém todos os prompts de todos os agentes"""
    try:
        agent_type = request.args.get('agent_type')
        prompts = prompt_manager.get_all_prompts(agent_type)
        return jsonify(prompts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts/<agent_type>/<prompt_type>', methods=['GET'])
def get_specific_prompt(agent_type, prompt_type):
    """Obtém um prompt específico"""
    try:
        prompt_text = prompt_manager.get_prompt(agent_type, prompt_type)
        return jsonify({'prompt_text': prompt_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    """Cria um novo prompt"""
    try:
        data = request.get_json()
        agent_type = data.get('agent_type')
        prompt_type = data.get('prompt_type')
        prompt_text = data.get('prompt_text')
        description = data.get('description')
        
        if not all([agent_type, prompt_type, prompt_text]):
            return jsonify({'error': 'Campos obrigatórios: agent_type, prompt_type, prompt_text'}), 400
        
        success = prompt_manager.create_prompt(agent_type, prompt_type, prompt_text, description)
        
        if success:
            return jsonify({'message': 'Prompt criado com sucesso'})
        else:
            return jsonify({'error': 'Falha ao criar prompt'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts', methods=['PUT'])
def update_prompt():
    """Atualiza um prompt existente"""
    try:
        data = request.get_json()
        agent_type = data.get('agent_type')
        prompt_type = data.get('prompt_type')
        prompt_text = data.get('prompt_text')
        description = data.get('description')
        
        if not all([agent_type, prompt_type, prompt_text]):
            return jsonify({'error': 'Campos obrigatórios: agent_type, prompt_type, prompt_text'}), 400
        
        success = prompt_manager.update_prompt(agent_type, prompt_type, prompt_text, description)
        
        if success:
            return jsonify({'message': 'Prompt atualizado com sucesso'})
        else:
            return jsonify({'error': 'Falha ao atualizar prompt'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts/<agent_type>/<prompt_type>', methods=['DELETE'])
def delete_prompt(agent_type, prompt_type):
    """Remove um prompt"""
    try:
        success = prompt_manager.delete_prompt(agent_type, prompt_type)
        
        if success:
            return jsonify({'message': 'Prompt removido com sucesso'})
        else:
            return jsonify({'error': 'Falha ao remover prompt'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts/reload', methods=['POST'])
def reload_prompts():
    """Recarrega o cache de prompts do Supabase"""
    try:
        prompt_manager.reload_cache()
        return jsonify({'message': 'Cache de prompts recarregado com sucesso'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PARA AGENTE DE PISOS ====================

@app.route('/api/pisos/search', methods=['POST'])
def search_pisos():
    """Busca semântica específica para pisos e revestimentos"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        threshold = data.get('threshold', 0.3)
        
        if not query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        # Buscar na base de conhecimento de pisos
        search_results = pisos_search_system.search(query, top_k, threshold)
        
        # Gerar resposta do agente de pisos
        agent_response = pisos_agent.generate_response(query, search_results)
        
        return jsonify({
            'query': query,
            'agent_response': agent_response,
            'search_results': search_results,
            'agent_type': 'pisos'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pisos/types', methods=['GET'])
def get_floor_types():
    """Retorna tipos de pisos disponíveis"""
    try:
        floor_type = request.args.get('type')
        top_k = int(request.args.get('top_k', 10))
        
        if floor_type:
            results = pisos_search_system.search_by_type(floor_type, top_k)
        else:
            # Retornar estatísticas dos tipos
            stats = pisos_search_system.get_statistics()
            return jsonify(stats)
        
        return jsonify({
            'floor_type': floor_type,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pisos/environments', methods=['GET'])
def get_floor_by_environment():
    """Retorna pisos adequados para um ambiente específico"""
    try:
        environment = request.args.get('environment')
        top_k = int(request.args.get('top_k', 10))
        
        if not environment:
            return jsonify({'error': 'Parâmetro environment é obrigatório'}), 400
        
        results = pisos_search_system.search_by_environment(environment, top_k)
        
        return jsonify({
            'environment': environment,
            'results': results,
            'count': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pisos/calculate', methods=['POST'])
def calculate_floor_materials():
    """Calcula quantidade de materiais para piso"""
    try:
        data = request.get_json()
        area = float(data.get('area', 0))
        floor_type = data.get('floor_type', 'ceramico')
        wastage_factor = float(data.get('wastage_factor', 0.1))
        
        if area <= 0:
            return jsonify({'error': 'Área deve ser maior que zero'}), 400
        
        calculation = pisos_agent.calculate_material_quantity(area, floor_type, wastage_factor)
        
        return jsonify({
            'input': {
                'area': area,
                'floor_type': floor_type,
                'wastage_factor': wastage_factor
            },
            'calculation': calculation
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pisos/diagnose', methods=['POST'])
def diagnose_floor_problem():
    """Diagnostica problemas em pisos"""
    try:
        data = request.get_json()
        problem_description = data.get('problem_description', '')
        
        if not problem_description:
            return jsonify({'error': 'Descrição do problema é obrigatória'}), 400
        
        diagnosis = pisos_agent.diagnose_problem(problem_description)
        
        return jsonify({
            'problem_description': problem_description,
            'diagnosis': diagnosis
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pisos/brands', methods=['GET'])
def get_floor_brands():
    """Retorna marcas principais por tipo de piso"""
    try:
        floor_type = request.args.get('type')
        
        if floor_type:
            brands = pisos_agent.get_brand_info(floor_type)
            return jsonify({
                'floor_type': floor_type,
                'brands': brands
            })
        else:
            return jsonify({
                'all_brands': pisos_agent.major_brands
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pisos/agent-info', methods=['GET'])
def get_pisos_agent_info():
    """Retorna informações do agente de pisos"""
    try:
        return jsonify(pisos_agent.get_agent_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PARA ORQUESTRADOR E REVISOR ====================

@app.route('/api/orchestrator/route', methods=['POST'])
def orchestrate_query():
    """Roteia consulta através do orquestrador inteligente"""
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        session_id = data.get('session_id')
        
        if not user_query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        # Rotear através do orquestrador
        routing_result = orchestrator_agent.route_query(user_query, session_id)
        
        return jsonify(routing_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orchestrator/capabilities', methods=['GET'])
def get_orchestrator_capabilities():
    """Retorna capacidades do orquestrador e agentes disponíveis"""
    try:
        return jsonify(orchestrator_agent.get_agent_capabilities())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orchestrator/stats', methods=['GET'])
def get_orchestrator_stats():
    """Retorna estatísticas de conversas do orquestrador"""
    try:
        return jsonify(orchestrator_agent.get_conversation_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orchestrator/clear-history', methods=['POST'])
def clear_orchestrator_history():
    """Limpa histórico de conversas do orquestrador"""
    try:
        data = request.get_json()
        session_id = data.get('session_id') if data else None
        
        orchestrator_agent.clear_conversation_history(session_id)
        
        message = f"Histórico {'da sessão ' + session_id if session_id else 'completo'} limpo com sucesso"
        return jsonify({'message': message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviewer/review', methods=['POST'])
def review_response():
    """Revisa uma resposta de agente especialista"""
    try:
        data = request.get_json()
        user_query = data.get('user_query', '')
        agent_response = data.get('agent_response', '')
        agent_type = data.get('agent_type', 'unknown')
        search_results = data.get('search_results', [])
        
        if not user_query or not agent_response:
            return jsonify({'error': 'user_query e agent_response são obrigatórios'}), 400
        
        # Revisar resposta
        review_result = reviewer_agent.review_response(
            user_query, agent_response, agent_type, search_results
        )
        
        return jsonify(review_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviewer/batch-review', methods=['POST'])
def batch_review_responses():
    """Revisa múltiplas respostas em lote"""
    try:
        data = request.get_json()
        responses = data.get('responses', [])
        
        if not responses:
            return jsonify({'error': 'Lista de responses é obrigatória'}), 400
        
        # Revisar em lote
        batch_result = reviewer_agent.batch_review(responses)
        
        return jsonify(batch_result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviewer/quality-report', methods=['GET'])
def get_quality_report():
    """Retorna relatório de qualidade geral"""
    try:
        return jsonify(reviewer_agent.get_quality_report())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviewer/improvement-suggestions', methods=['GET'])
def get_improvement_suggestions():
    """Retorna sugestões de melhoria para um agente"""
    try:
        agent_type = request.args.get('agent_type')
        time_period = int(request.args.get('time_period_days', 30))
        
        if not agent_type:
            return jsonify({'error': 'Parâmetro agent_type é obrigatório'}), 400
        
        suggestions = reviewer_agent.get_improvement_suggestions(agent_type, time_period)
        
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reviewer/agent-info', methods=['GET'])
def get_reviewer_agent_info():
    """Retorna informações do agente revisor"""
    try:
        return jsonify(reviewer_agent.get_agent_info())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINT INTEGRADO COM ORQUESTRAÇÃO E REVISÃO ====================

@app.route('/api/smart-chat', methods=['POST'])
def smart_chat():
    """
    Endpoint inteligente que combina orquestração, busca especializada e revisão
    """
    try:
        data = request.get_json()
        user_query = data.get('query', '')
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        enable_review = data.get('enable_review', True)
        
        if not user_query:
            return jsonify({'error': 'Query é obrigatória'}), 400
        
        # 1. Orquestração - Identificar agente apropriado
        routing_result = orchestrator_agent.route_query(user_query, session_id)
        selected_agent = routing_result["routing_analysis"]["selected_agent"]
        
        # 2. Busca especializada no agente identificado
        if selected_agent == "tintas":
            search_results = search_system.search(user_query, top_k=5)
            # Aqui você poderia usar o agente de tintas para gerar resposta
            agent_response = f"Resposta do agente de tintas para: {user_query}"
        elif selected_agent == "pisos":
            search_results = pisos_search_system.search(user_query, top_k=5)
            agent_response = pisos_agent.generate_response(user_query, search_results)
        else:
            search_results = []
            agent_response = "Agente não identificado corretamente."
        
        # 3. Revisão da resposta (se habilitada)
        review_result = None
        if enable_review:
            review_result = reviewer_agent.review_response(
                user_query, agent_response, selected_agent, search_results
            )
            
            # Usar resposta melhorada se disponível
            if review_result.get("improved_response"):
                agent_response = review_result["improved_response"]
        
        # 4. Resposta final integrada
        return jsonify({
            "user_query": user_query,
            "session_id": session_id,
            "routing": routing_result,
            "agent_response": agent_response,
            "search_results": search_results,
            "review": review_result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PARA UPLOAD E PROCESSAMENTO DE PDFs ====================

@app.route('/api/upload/pdf', methods=['POST'])
def upload_pdf():
    """Upload de arquivo PDF para processamento"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        agent_type = request.form.get('agent_type', 'general')
        
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Salvar arquivo
        file_info = pdf_processor.save_uploaded_file(file, agent_type)
        
        return jsonify({
            'message': 'Arquivo enviado com sucesso',
            'file_info': file_info
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/process/<file_id>', methods=['POST'])
def process_pdf(file_id):
    """Processa PDF enviado e extrai informações"""
    try:
        # Buscar informações do arquivo
        file_info = None
        for result in pdf_processor.processing_history:
            if result.get('file_id') == file_id:
                file_info = result
                break
        
        if not file_info:
            # Criar file_info básico se não encontrado no histórico
            file_path = None
            for filename in os.listdir(pdf_processor.upload_folder):
                if filename.startswith(file_id):
                    file_path = os.path.join(pdf_processor.upload_folder, filename)
                    break
            
            if not file_path:
                return jsonify({'error': 'Arquivo não encontrado'}), 404
            
            file_info = {
                'file_id': file_id,
                'file_path': file_path,
                'agent_type': request.json.get('agent_type', 'general') if request.json else 'general'
            }
        
        # Processar arquivo
        processing_result = pdf_processor.process_uploaded_pdf(file_info)
        
        return jsonify({
            'message': 'Processamento concluído',
            'result': processing_result
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/history', methods=['GET'])
def get_upload_history():
    """Retorna histórico de uploads e processamentos"""
    try:
        limit = int(request.args.get('limit', 50))
        history = pdf_processor.get_processing_history(limit)
        
        return jsonify({
            'history': history,
            'count': len(history)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/products/<file_id>', methods=['GET'])
def get_processed_products(file_id):
    """Retorna produtos extraídos de um arquivo específico"""
    try:
        products = pdf_processor.get_processed_products(file_id)
        
        return jsonify({
            'file_id': file_id,
            'products': products,
            'count': len(products)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/stats', methods=['GET'])
def get_upload_stats():
    """Retorna estatísticas de uploads"""
    try:
        stats = pdf_processor.get_upload_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/cleanup', methods=['POST'])
def cleanup_temp_files():
    """Remove arquivos temporários antigos"""
    try:
        data = request.get_json()
        older_than_hours = data.get('older_than_hours', 24) if data else 24
        
        pdf_processor.cleanup_temp_files(older_than_hours)
        
        return jsonify({'message': f'Limpeza concluída. Arquivos mais antigos que {older_than_hours}h foram removidos.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload/integrate-products', methods=['POST'])
def integrate_processed_products():
    """Integra produtos processados à base de conhecimento"""
    try:
        data = request.get_json()
        file_id = data.get('file_id')
        agent_type = data.get('agent_type', 'general')
        
        if not file_id:
            return jsonify({'error': 'file_id é obrigatório'}), 400
        
        # Obter produtos processados
        products = pdf_processor.get_processed_products(file_id)
        
        if not products:
            return jsonify({'error': 'Nenhum produto encontrado para este arquivo'}), 404
        
        # Integrar à base de conhecimento apropriada
        integrated_count = 0
        
        if agent_type == "tintas":
            # Adicionar à base de conhecimento de tintas
            for product in products:
                search_system.add_knowledge_item(product)
                integrated_count += 1
        
        elif agent_type == "pisos":
            # Adicionar à base de conhecimento de pisos
            for product in products:
                pisos_search_system.add_knowledge_item(product)
                integrated_count += 1
        
        else:
            # Adicionar a ambas as bases (produtos genéricos)
            for product in products:
                search_system.add_knowledge_item(product)
                pisos_search_system.add_knowledge_item(product)
                integrated_count += 1
        
        return jsonify({
            'message': f'{integrated_count} produtos integrados com sucesso à base de conhecimento',
            'integrated_count': integrated_count,
            'agent_type': agent_type
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PARA EDITOR DE BASE DE CONHECIMENTO ====================

@app.route('/api/knowledge/items', methods=['GET'])
def get_knowledge_items():
    """Retorna itens de conhecimento com filtros opcionais"""
    try:
        agent_type = request.args.get('agent_type')
        category = request.args.get('category')
        query = request.args.get('query')
        tags = request.args.getlist('tags')
        status = request.args.get('status')
        
        if query or tags or status:
            # Busca com filtros
            items = knowledge_editor.search_knowledge(
                query=query,
                agent_type=agent_type,
                category=category,
                tags=tags,
                status=status
            )
        elif agent_type and category:
            # Busca por categoria específica
            items = knowledge_editor.get_knowledge_by_category(agent_type, category)
        elif agent_type:
            # Busca por agente
            items = knowledge_editor.get_knowledge_by_agent(agent_type)
        else:
            # Busca geral
            items = []
            for agent in ['tintas', 'pisos', 'geral']:
                agent_items = knowledge_editor.get_knowledge_by_agent(agent)
                for cat, cat_items in agent_items.items():
                    items.extend(cat_items)
        
        return jsonify({
            'items': items,
            'count': len(items) if isinstance(items, list) else sum(len(cat_items) for cat_items in items.values())
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/items', methods=['POST'])
def create_knowledge_item():
    """Cria um novo item de conhecimento"""
    try:
        data = request.get_json()
        
        # Validar dados
        validation = knowledge_editor.validate_knowledge_item(data)
        if not validation['valid']:
            return jsonify({
                'error': 'Dados inválidos',
                'validation': validation
            }), 400
        
        # Criar item
        item = knowledge_editor.create_knowledge_item(
            title=data['title'],
            content=data['content'],
            category=data['category'],
            agent_type=data['agent_type'],
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            template_type=data.get('template_type')
        )
        
        return jsonify({
            'message': 'Item criado com sucesso',
            'item': asdict(item),
            'validation': validation
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/items/<item_id>', methods=['GET'])
def get_knowledge_item(item_id):
    """Retorna um item específico de conhecimento"""
    try:
        item = knowledge_editor.find_knowledge_item(item_id)
        
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        return jsonify({'item': asdict(item)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/items/<item_id>', methods=['PUT'])
def update_knowledge_item(item_id):
    """Atualiza um item de conhecimento"""
    try:
        data = request.get_json()
        
        # Validar dados se fornecidos
        if any(key in data for key in ['title', 'content', 'category', 'agent_type']):
            validation = knowledge_editor.validate_knowledge_item(data)
            if not validation['valid']:
                return jsonify({
                    'error': 'Dados inválidos',
                    'validation': validation
                }), 400
        
        # Atualizar item
        item = knowledge_editor.update_knowledge_item(
            item_id=item_id,
            title=data.get('title'),
            content=data.get('content'),
            category=data.get('category'),
            tags=data.get('tags'),
            metadata=data.get('metadata'),
            status=data.get('status')
        )
        
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        return jsonify({
            'message': 'Item atualizado com sucesso',
            'item': asdict(item)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/items/<item_id>', methods=['DELETE'])
def delete_knowledge_item(item_id):
    """Remove um item de conhecimento"""
    try:
        success = knowledge_editor.delete_knowledge_item(item_id)
        
        if not success:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        return jsonify({'message': 'Item removido com sucesso'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/items/<item_id>/duplicate', methods=['POST'])
def duplicate_knowledge_item(item_id):
    """Duplica um item de conhecimento"""
    try:
        data = request.get_json()
        new_title = data.get('new_title') if data else None
        
        item = knowledge_editor.duplicate_knowledge_item(item_id, new_title)
        
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        return jsonify({
            'message': 'Item duplicado com sucesso',
            'item': asdict(item)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/categories', methods=['GET'])
def get_knowledge_categories():
    """Retorna categorias disponíveis"""
    try:
        agent_type = request.args.get('agent_type')
        categories = knowledge_editor.get_available_categories(agent_type)
        
        return jsonify({
            'categories': categories,
            'all_categories': knowledge_editor.categories
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/templates', methods=['GET'])
def get_knowledge_templates():
    """Retorna templates disponíveis"""
    try:
        templates = knowledge_editor.get_available_templates()
        return jsonify({'templates': templates})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/stats', methods=['GET'])
def get_knowledge_stats():
    """Retorna estatísticas da base de conhecimento"""
    try:
        stats = knowledge_editor.get_knowledge_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/export', methods=['GET'])
def export_knowledge():
    """Exporta base de conhecimento"""
    try:
        agent_type = request.args.get('agent_type')
        format_type = request.args.get('format', 'json')
        
        exported_data = knowledge_editor.export_knowledge(agent_type, format_type)
        
        return jsonify({
            'data': exported_data,
            'agent_type': agent_type,
            'format': format_type,
            'exported_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/import', methods=['POST'])
def import_knowledge():
    """Importa base de conhecimento"""
    try:
        data = request.get_json()
        
        if not data or 'data' not in data or 'agent_type' not in data:
            return jsonify({'error': 'Dados e agent_type são obrigatórios'}), 400
        
        result = knowledge_editor.import_knowledge(
            data=data['data'],
            agent_type=data['agent_type'],
            merge=data.get('merge', True)
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/knowledge/validate', methods=['POST'])
def validate_knowledge_item():
    """Valida um item de conhecimento"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados são obrigatórios'}), 400
        
        validation = knowledge_editor.validate_knowledge_item(data)
        
        return jsonify(validation)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ENDPOINTS PARA VERSIONAMENTO ====================

@app.route('/api/versions/items/<item_id>', methods=['GET'])
def get_item_versions(item_id):
    """Retorna histórico de versões de um item"""
    try:
        limit = int(request.args.get('limit', 50))
        versions = version_manager.get_version_history(item_id, limit)
        
        return jsonify({
            'item_id': item_id,
            'versions': [asdict(v) for v in versions],
            'count': len(versions)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/items/<item_id>/current', methods=['GET'])
def get_current_item_version(item_id):
    """Retorna a versão atual de um item"""
    try:
        version = version_manager.get_current_version(item_id)
        
        if not version:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        return jsonify({'version': asdict(version)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/<version_id>', methods=['GET'])
def get_version_by_id(version_id):
    """Retorna uma versão específica pelo ID"""
    try:
        version = version_manager.get_version_by_id(version_id)
        
        if not version:
            return jsonify({'error': 'Versão não encontrada'}), 404
        
        return jsonify({'version': asdict(version)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions', methods=['POST'])
def create_version():
    """Cria uma nova versão de um item"""
    try:
        data = request.get_json()
        
        required_fields = ['item_id', 'item_type', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        version = version_manager.create_version(
            item_id=data['item_id'],
            item_type=data['item_type'],
            content=data['content'],
            changes_summary=data.get('changes_summary', 'Nova versão'),
            created_by=data.get('created_by', 'system'),
            tags=data.get('tags', []),
            parent_version_id=data.get('parent_version_id')
        )
        
        return jsonify({
            'message': 'Versão criada com sucesso',
            'version': asdict(version)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/rollback', methods=['POST'])
def rollback_version():
    """Faz rollback para uma versão específica"""
    try:
        data = request.get_json()
        
        required_fields = ['item_id', 'target_version_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        version = version_manager.rollback_to_version(
            item_id=data['item_id'],
            target_version_id=data['target_version_id'],
            rollback_by=data.get('rollback_by', 'system'),
            rollback_reason=data.get('rollback_reason', 'Rollback solicitado')
        )
        
        if not version:
            return jsonify({'error': 'Não foi possível fazer rollback'}), 400
        
        return jsonify({
            'message': 'Rollback realizado com sucesso',
            'version': asdict(version)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/compare', methods=['POST'])
def compare_versions():
    """Compara duas versões"""
    try:
        data = request.get_json()
        
        required_fields = ['version_id_1', 'version_id_2']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        comparison = version_manager.compare_versions(
            data['version_id_1'],
            data['version_id_2']
        )
        
        return jsonify(comparison)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/branches', methods=['POST'])
def create_branch():
    """Cria uma branch a partir de uma versão"""
    try:
        data = request.get_json()
        
        required_fields = ['base_version_id', 'branch_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        branch_version = version_manager.create_branch(
            base_version_id=data['base_version_id'],
            branch_name=data['branch_name'],
            created_by=data.get('created_by', 'system')
        )
        
        if not branch_version:
            return jsonify({'error': 'Não foi possível criar a branch'}), 400
        
        return jsonify({
            'message': 'Branch criada com sucesso',
            'branch_version': asdict(branch_version)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/merge', methods=['POST'])
def merge_branch():
    """Faz merge de uma branch com o item principal"""
    try:
        data = request.get_json()
        
        required_fields = ['main_item_id', 'branch_item_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        merged_version = version_manager.merge_branch(
            main_item_id=data['main_item_id'],
            branch_item_id=data['branch_item_id'],
            merge_by=data.get('merge_by', 'system'),
            merge_strategy=data.get('merge_strategy', 'overwrite')
        )
        
        if not merged_version:
            return jsonify({'error': 'Não foi possível fazer merge'}), 400
        
        return jsonify({
            'message': 'Merge realizado com sucesso',
            'merged_version': asdict(merged_version)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/tags', methods=['POST'])
def tag_version():
    """Adiciona tags a uma versão"""
    try:
        data = request.get_json()
        
        required_fields = ['version_id', 'tags']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        success = version_manager.tag_version(
            version_id=data['version_id'],
            tags=data['tags']
        )
        
        if not success:
            return jsonify({'error': 'Versão não encontrada'}), 404
        
        return jsonify({'message': 'Tags adicionadas com sucesso'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/tags/<tag>', methods=['GET'])
def get_versions_by_tag(tag):
    """Retorna versões que possuem uma tag específica"""
    try:
        versions = version_manager.get_versions_by_tag(tag)
        
        return jsonify({
            'tag': tag,
            'versions': [asdict(v) for v in versions],
            'count': len(versions)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/logs', methods=['GET'])
def get_change_logs():
    """Retorna logs de mudanças com filtros opcionais"""
    try:
        item_id = request.args.get('item_id')
        user = request.args.get('user')
        action = request.args.get('action')
        limit = int(request.args.get('limit', 100))
        
        logs = version_manager.get_change_logs(
            item_id=item_id,
            user=user,
            action=action,
            limit=limit
        )
        
        return jsonify({
            'logs': [asdict(log) for log in logs],
            'count': len(logs),
            'filters': {
                'item_id': item_id,
                'user': user,
                'action': action,
                'limit': limit
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/stats', methods=['GET'])
def get_version_stats():
    """Retorna estatísticas de versionamento"""
    try:
        stats = version_manager.get_version_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/export', methods=['GET'])
def export_versions():
    """Exporta versões em formato JSON"""
    try:
        item_id = request.args.get('item_id')
        exported_data = version_manager.export_versions(item_id)
        
        return jsonify({
            'data': exported_data,
            'item_id': item_id,
            'exported_at': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/versions/import', methods=['POST'])
def import_versions():
    """Importa versões de formato JSON"""
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({'error': 'Dados são obrigatórios'}), 400
        
        result = version_manager.import_versions(data['data'])
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'message': 'API do Agente Especialista em Tintas está funcionando',
        'services': {
            'tintas_knowledge_base_size': len(search_system.knowledge_base),
            'pisos_knowledge_base_size': len(pisos_search_system.knowledge_base),
            'products_count': len(product_manager.get_all_products()),
            'supabase_connected': supabase_manager.is_connected(),
            'evolution_api_configured': evolution_client.is_configured(),
            'prompts_loaded': len(prompt_manager.get_all_prompts()),
            'agents_available': ['tintas', 'pisos', 'orquestrador', 'revisor'],
            'orchestrator_openai': orchestrator_agent._is_openai_available(),
            'reviewer_openai': reviewer_agent._is_openai_available()
        },
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask integrado...")
    print("📊 Sistemas disponíveis:")
    print(f"   - Busca Semântica: {len(search_system.knowledge_base)} itens")
    print(f"   - Produtos: {len(product_manager.get_all_products())} itens")
    print(f"   - Supabase: {'✅ Conectado' if supabase_manager.is_connected() else '❌ Não conectado'}")
    print(f"   - Evolution API: {'✅ Configurada' if evolution_client.is_configured() else '❌ Não configurada'}")
    print("🌐 Servidor rodando em http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
