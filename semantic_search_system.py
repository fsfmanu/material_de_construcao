import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class SemanticSearchSystem:
    def __init__(self, knowledge_base_path, model_name='all-MiniLM-L6-v2'):
        """
        Inicializa o sistema de busca semântica
        
        Args:
            knowledge_base_path: Caminho para o arquivo JSON da base de conhecimento
            model_name: Nome do modelo de embeddings a ser usado
        """
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = self.load_knowledge_base(knowledge_base_path)
        self.embeddings = None
        self.documents = []
        self.embeddings_file = 'knowledge_embeddings.pkl'
        
        # Preparar documentos para busca
        self.prepare_documents()
        
        # Carregar ou criar embeddings
        if os.path.exists(self.embeddings_file):
            self.load_embeddings()
        else:
            self.create_embeddings()
    
    def load_knowledge_base(self, path):
        """Carrega a base de conhecimento do arquivo JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def prepare_documents(self):
        """Prepara os documentos para busca semântica"""
        self.documents = []
        for item in self.knowledge_base:
            # Criar um documento combinando todas as informações relevantes
            doc_text = f"""
            Marca: {item.get('brand', '')}
            Produto: {item.get('product_name', '')}
            Tipo: {item.get('type', '')}
            Rendimento: {item.get('coverage', '')}
            Tempo de Secagem: {item.get('drying_time', '')}
            Diluição: {item.get('dilution', '')}
            Ferramentas: {' '.join(item.get('application_tools', []))}
            Casos de Uso: {' '.join(item.get('use_case', []))}
            Características: {' '.join(item.get('features', []))}
            Descrição: {item.get('description', '')}
            """.strip()
            
            self.documents.append({
                'text': doc_text,
                'metadata': item
            })
    
    def create_embeddings(self):
        """Cria embeddings para todos os documentos"""
        print("Criando embeddings para a base de conhecimento...")
        texts = [doc['text'] for doc in self.documents]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Salvar embeddings para uso futuro
        with open(self.embeddings_file, 'wb') as f:
            pickle.dump(self.embeddings, f)
        print(f"Embeddings salvos em {self.embeddings_file}")
    
    def load_embeddings(self):
        """Carrega embeddings salvos"""
        print("Carregando embeddings existentes...")
        with open(self.embeddings_file, 'rb') as f:
            self.embeddings = pickle.load(f)
    
    def search(self, query, top_k=5, similarity_threshold=0.3):
        """
        Realiza busca semântica na base de conhecimento
        
        Args:
            query: Consulta do usuário
            top_k: Número máximo de resultados a retornar
            similarity_threshold: Limiar mínimo de similaridade
            
        Returns:
            Lista de resultados ordenados por relevância
        """
        # Criar embedding da consulta
        query_embedding = self.model.encode([query])
        
        # Calcular similaridades
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Obter índices dos documentos mais similares
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filtrar por limiar de similaridade
        results = []
        for idx in top_indices:
            similarity_score = similarities[idx]
            if similarity_score >= similarity_threshold:
                results.append({
                    'document': self.documents[idx]['metadata'],
                    'similarity_score': float(similarity_score),
                    'text_snippet': self.documents[idx]['text'][:200] + "..."
                })
        
        return results
    
    def search_by_category(self, query, category_filter=None, top_k=5):
        """
        Busca com filtro por categoria
        
        Args:
            query: Consulta do usuário
            category_filter: Filtro por categoria (brand, type, etc.)
            top_k: Número máximo de resultados
        """
        results = self.search(query, top_k=top_k * 2)  # Buscar mais para filtrar
        
        if category_filter:
            filtered_results = []
            for result in results:
                doc = result['document']
                if any(category_filter.lower() in str(value).lower() 
                      for value in doc.values() if value):
                    filtered_results.append(result)
            results = filtered_results[:top_k]
        
        return results
    
    def get_product_recommendations(self, user_requirements):
        """
        Recomenda produtos baseado nos requisitos do usuário
        
        Args:
            user_requirements: Dicionário com requisitos (tipo, uso, características)
        """
        # Construir consulta baseada nos requisitos
        query_parts = []
        
        if 'tipo' in user_requirements:
            query_parts.append(f"tipo {user_requirements['tipo']}")
        
        if 'uso' in user_requirements:
            query_parts.append(f"uso {user_requirements['uso']}")
        
        if 'características' in user_requirements:
            query_parts.extend(user_requirements['características'])
        
        if 'ambiente' in user_requirements:
            query_parts.append(f"ambiente {user_requirements['ambiente']}")
        
        query = " ".join(query_parts)
        
        return self.search(query, top_k=3, similarity_threshold=0.2)
    
    def explain_search_results(self, query, results):
        """
        Explica por que determinados resultados foram retornados
        """
        explanation = f"Para a consulta '{query}', encontrei {len(results)} resultado(s) relevante(s):\n\n"
        
        for i, result in enumerate(results, 1):
            doc = result['document']
            score = result['similarity_score']
            
            explanation += f"{i}. **{doc.get('product_name', 'Produto')}** da {doc.get('brand', 'Marca')} "
            explanation += f"(Similaridade: {score:.2f})\n"
            explanation += f"   - Tipo: {doc.get('type', 'N/A')}\n"
            explanation += f"   - Características: {', '.join(doc.get('features', [])[:3])}\n"
            explanation += f"   - Casos de uso: {', '.join(doc.get('use_case', [])[:3])}\n\n"
        
        return explanation

def test_semantic_search():
    """Função de teste do sistema de busca semântica"""
    print("Inicializando sistema de busca semântica...")
    
    # Inicializar o sistema
    search_system = SemanticSearchSystem('/home/ubuntu/structured_knowledge_refined.json')
    
    # Testes de busca
    test_queries = [
        "tinta para parede interna lavável",
        "produto coral para madeira",
        "tinta acrílica premium",
        "esmalte para metal",
        "tinta sem cheiro para quarto",
        "produto suvinil fosco"
    ]
    
    print("\n=== TESTES DE BUSCA SEMÂNTICA ===\n")
    
    for query in test_queries:
        print(f"Consulta: '{query}'")
        results = search_system.search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                doc = result['document']
                score = result['similarity_score']
                print(f"  {i}. {doc.get('product_name', 'N/A')} ({doc.get('brand', 'N/A')}) - Score: {score:.3f}")
        else:
            print("  Nenhum resultado encontrado.")
        print()
    
    # Teste de recomendação
    print("=== TESTE DE RECOMENDAÇÃO ===\n")
    requirements = {
        'tipo': 'residencial',
        'uso': ['internas', 'paredes'],
        'características': ['lavável', 'sem cheiro'],
        'ambiente': 'quarto'
    }
    
    recommendations = search_system.get_product_recommendations(requirements)
    print(f"Recomendações para: {requirements}")
    
    for i, rec in enumerate(recommendations, 1):
        doc = rec['document']
        score = rec['similarity_score']
        print(f"  {i}. {doc.get('product_name', 'N/A')} ({doc.get('brand', 'N/A')}) - Score: {score:.3f}")
    
    return search_system

if __name__ == "__main__":
    search_system = test_semantic_search()
