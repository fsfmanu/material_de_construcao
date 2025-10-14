from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import json
from datetime import datetime

# Adicionar o diretório pai ao path para importar o sistema de busca semântica
sys.path.append('/home/ubuntu')
from semantic_search_system import SemanticSearchSystem
from product_manager import product_manager
from supabase_client import supabase_manager
from evolution_api_client import evolution_client
from whatsapp_service import whatsapp_service

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend React

# Inicializar sistemas
print("Inicializando sistemas...")
search_system = SemanticSearchSystem('/home/ubuntu/structured_knowledge_refined.json')
print(f"✅ Sistema de busca semântica inicializado com {len(search_system.knowledge_base)} itens")
print(f"✅ Gerenciador de produtos inicializado com {len(product_manager.get_all_products())} produtos")
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
    
    # Resposta base
    response = "Olá! Sou seu especialista em tintas com 20 anos de experiência. "
    
    if search_results:
        # Se encontrou produtos relevantes
        response += f"Encontrei {len(search_results)} produto(s) relevante(s) para sua consulta:\n\n"
        
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
        response += "\n💰 **Para elaborar um orçamento preciso, preciso saber:**\n"
        response += "1. Tipo de projeto (residencial/automotivo)\n"
        response += "2. Superfície a pintar\n"
        response += "3. Área em m²\n"
        response += "4. Condições do ambiente\n"
        response += "5. Acabamento desejado\n\n"
        response += "Você pode me fornecer essas informações?"
    
    elif 'descasca' in message_lower or 'problema' in message_lower:
        response += "\n🔧 **Problemas de descascamento geralmente indicam:**\n"
        response += "1. Superfície mal preparada (80% dos casos)\n"
        response += "2. Presença de umidade\n"
        response += "3. Incompatibilidade química entre produtos\n\n"
        response += "**Recomendo:** Remoção completa das camadas soltas, tratamento da umidade na fonte e aplicação de primer adequado."
    
    elif 'calcul' in message_lower or 'quantidade' in message_lower:
        response += "\n📐 **Para calcular a tinta necessária:**\n"
        response += "- Área Total = (Largura × Altura × Paredes) - Vãos\n"
        response += "- Litros = Área ÷ Rendimento ÷ Demãos + 10% para perdas\n\n"
        response += "Qual a área que você precisa pintar?"
    
    elif not search_results:
        response += "Não encontrei produtos específicos para sua consulta, mas posso ajudá-lo com:\n\n"
        response += "🎨 **Recomendações de produtos**\n"
        response += "📊 **Cálculo de materiais**\n"
        response += "🔧 **Solução de problemas**\n"
        response += "💰 **Orçamentos personalizados**\n"
        response += "🌈 **Escolha de cores e sistemas de pintura**\n\n"
        response += "Qual sua necessidade específica?"
    
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'healthy',
        'message': 'API do Agente Especialista em Tintas está funcionando',
        'services': {
            'knowledge_base_size': len(search_system.knowledge_base),
            'products_count': len(product_manager.get_all_products()),
            'supabase_connected': supabase_manager.is_connected(),
            'evolution_api_configured': evolution_client.is_configured()
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
