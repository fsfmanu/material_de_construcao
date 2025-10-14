"""
Sistema de Busca Semântica para Pisos e Revestimentos
Especializado em encontrar informações relevantes sobre pisos, revestimentos e materiais relacionados.
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Any, Optional
import re

class PisosSemanticSearch:
    def __init__(self, knowledge_base_path: str = None):
        """
        Inicializa o sistema de busca semântica para pisos
        
        Args:
            knowledge_base_path: Caminho para a base de conhecimento em JSON
        """
        print("🔍 Inicializando sistema de busca semântica para pisos...")
        
        # Carregar modelo de embeddings
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # Base de conhecimento específica de pisos
        self.knowledge_base = []
        self.embeddings = None
        
        # Carregar base de conhecimento
        if knowledge_base_path:
            self._load_knowledge_base(knowledge_base_path)
        else:
            self._create_default_knowledge_base()
        
        # Gerar embeddings
        self._generate_embeddings()
        
        print(f"✅ Sistema de busca para pisos inicializado com {len(self.knowledge_base)} itens")

    def _load_knowledge_base(self, path: str):
        """Carrega base de conhecimento de arquivo JSON"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.knowledge_base = data if isinstance(data, list) else [data]
        except FileNotFoundError:
            print(f"⚠️  Arquivo não encontrado: {path}. Usando base padrão.")
            self._create_default_knowledge_base()
        except json.JSONDecodeError:
            print(f"⚠️  Erro ao decodificar JSON: {path}. Usando base padrão.")
            self._create_default_knowledge_base()

    def _create_default_knowledge_base(self):
        """Cria base de conhecimento padrão para pisos"""
        self.knowledge_base = [
            {
                "id": "ceramico_001",
                "product_name": "Piso Cerâmico Esmaltado",
                "brand": "Eliane",
                "type": "Cerâmico",
                "category": "Revestimento",
                "size": "45x45cm",
                "pei_class": 3,
                "slip_resistance": "R10",
                "water_absorption": "10-20%",
                "features": ["Esmaltado", "Fácil limpeza", "Custo benefício"],
                "use_case": ["Sala", "Quarto", "Cozinha"],
                "price_range": "R$ 15-30/m²",
                "installation": "Argamassa colante",
                "maintenance": "Limpeza diária com pano úmido",
                "description": "Piso cerâmico esmaltado ideal para ambientes residenciais, oferece ótimo custo-benefício e facilidade de manutenção."
            },
            {
                "id": "porcelanato_001",
                "product_name": "Porcelanato Polido Mármore Carrara",
                "brand": "Portinari",
                "type": "Porcelanato",
                "category": "Revestimento",
                "size": "60x60cm",
                "pei_class": 4,
                "slip_resistance": "R9",
                "water_absorption": "<0.5%",
                "features": ["Polido", "Baixa absorção", "Elegante", "Durável"],
                "use_case": ["Sala", "Hall", "Escritório"],
                "price_range": "R$ 45-80/m²",
                "installation": "Argamassa colante AC-III",
                "maintenance": "Limpeza com produtos neutros",
                "description": "Porcelanato polido que reproduz a beleza do mármore Carrara, ideal para ambientes sofisticados."
            },
            {
                "id": "porcelanato_002",
                "product_name": "Porcelanato Acetinado Madeira",
                "brand": "Biancogres",
                "type": "Porcelanato",
                "category": "Revestimento",
                "size": "20x120cm",
                "pei_class": 4,
                "slip_resistance": "R10",
                "water_absorption": "<0.5%",
                "features": ["Acetinado", "Efeito madeira", "Antiderrapante"],
                "use_case": ["Sala", "Quarto", "Varanda"],
                "price_range": "R$ 50-90/m²",
                "installation": "Argamassa colante flexível",
                "maintenance": "Aspirar e passar pano úmido",
                "description": "Porcelanato que reproduz fielmente a textura da madeira, com toda a praticidade do porcelanato."
            },
            {
                "id": "laminado_001",
                "product_name": "Piso Laminado Click Carvalho",
                "brand": "Durafloor",
                "type": "Laminado",
                "category": "Piso",
                "size": "19.7x121cm",
                "pei_class": 4,
                "slip_resistance": "R9",
                "water_absorption": "Sensível à umidade",
                "features": ["Sistema click", "Fácil instalação", "Confortável"],
                "use_case": ["Quarto", "Sala", "Escritório"],
                "price_range": "R$ 35-65/m²",
                "installation": "Instalação flutuante com manta",
                "maintenance": "Aspirar e limpar com produto específico",
                "description": "Piso laminado com sistema de encaixe click, reproduz a beleza natural do carvalho."
            },
            {
                "id": "vinilico_001",
                "product_name": "Piso Vinílico LVT Carvalho Rústico",
                "brand": "Tarkett",
                "type": "Vinílico",
                "category": "Piso",
                "size": "18.4x122cm",
                "pei_class": 5,
                "slip_resistance": "R10",
                "water_absorption": "Impermeável",
                "features": ["100% impermeável", "Confortável", "Isolamento acústico"],
                "use_case": ["Cozinha", "Banheiro", "Área de serviço"],
                "price_range": "R$ 40-70/m²",
                "installation": "Colagem total ou click",
                "maintenance": "Limpeza diária com pano úmido",
                "description": "Piso vinílico de luxo totalmente impermeável, ideal para áreas molhadas."
            },
            {
                "id": "madeira_001",
                "product_name": "Piso de Madeira Maciça Cumaru",
                "brand": "Indusparquet",
                "type": "Madeira",
                "category": "Piso",
                "size": "7x10x100cm",
                "pei_class": 5,
                "slip_resistance": "R11",
                "water_absorption": "Sensível à umidade",
                "features": ["Madeira nativa", "Durável", "Elegante", "Natural"],
                "use_case": ["Sala", "Quarto", "Escritório"],
                "price_range": "R$ 80-150/m²",
                "installation": "Pregado ou colado",
                "maintenance": "Enceramento periódico",
                "description": "Piso de madeira maciça cumaru, oferece beleza natural e alta durabilidade."
            },
            {
                "id": "pedra_001",
                "product_name": "Mármore Branco Paraná",
                "brand": "Pedras Naturais",
                "type": "Pedra Natural",
                "category": "Revestimento",
                "size": "Sob medida",
                "pei_class": 3,
                "slip_resistance": "R9",
                "water_absorption": "5-10%",
                "features": ["Natural", "Elegante", "Único", "Luxuoso"],
                "use_case": ["Hall", "Banheiro", "Bancada"],
                "price_range": "R$ 60-120/m²",
                "installation": "Argamassa específica",
                "maintenance": "Impermeabilização e limpeza específica",
                "description": "Mármore natural brasileiro, ideal para ambientes sofisticados e únicos."
            },
            {
                "id": "cimento_001",
                "product_name": "Piso de Cimento Queimado",
                "brand": "Artesanal",
                "type": "Cimento",
                "category": "Revestimento",
                "size": "Contínuo",
                "pei_class": 4,
                "slip_resistance": "R11",
                "water_absorption": "Poroso",
                "features": ["Industrial", "Moderno", "Econômico", "Versátil"],
                "use_case": ["Sala", "Cozinha", "Área externa"],
                "price_range": "R$ 25-45/m²",
                "installation": "Aplicação direta",
                "maintenance": "Impermeabilização periódica",
                "description": "Piso de cimento queimado, ideal para ambientes com estilo industrial e moderno."
            }
        ]

    def _generate_embeddings(self):
        """Gera embeddings para todos os itens da base de conhecimento"""
        if not self.knowledge_base:
            return
        
        # Criar textos para embedding combinando campos relevantes
        texts = []
        for item in self.knowledge_base:
            text_parts = [
                item.get('product_name', ''),
                item.get('brand', ''),
                item.get('type', ''),
                item.get('description', ''),
                ' '.join(item.get('features', [])),
                ' '.join(item.get('use_case', []))
            ]
            text = ' '.join(filter(None, text_parts))
            texts.append(text)
        
        # Gerar embeddings
        self.embeddings = self.model.encode(texts)

    def search(self, query: str, top_k: int = 5, similarity_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Busca semântica na base de conhecimento de pisos
        
        Args:
            query: Consulta do usuário
            top_k: Número máximo de resultados
            similarity_threshold: Limiar mínimo de similaridade
            
        Returns:
            Lista de resultados ordenados por relevância
        """
        if not self.embeddings.size:
            return []
        
        # Gerar embedding da consulta
        query_embedding = self.model.encode([query])
        
        # Calcular similaridades
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Encontrar índices dos resultados mais similares
        similar_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in similar_indices[:top_k]:
            similarity_score = similarities[idx]
            
            if similarity_score >= similarity_threshold:
                result = {
                    'document': self.knowledge_base[idx],
                    'similarity_score': float(similarity_score),
                    'index': int(idx)
                }
                results.append(result)
        
        return results

    def search_by_type(self, floor_type: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Busca produtos por tipo específico de piso
        
        Args:
            floor_type: Tipo de piso (ceramico, porcelanato, laminado, etc.)
            top_k: Número máximo de resultados
            
        Returns:
            Lista de produtos do tipo especificado
        """
        results = []
        floor_type_lower = floor_type.lower()
        
        for idx, item in enumerate(self.knowledge_base):
            item_type = item.get('type', '').lower()
            if floor_type_lower in item_type or item_type in floor_type_lower:
                result = {
                    'document': item,
                    'similarity_score': 1.0,  # Correspondência exata
                    'index': idx
                }
                results.append(result)
                
                if len(results) >= top_k:
                    break
        
        return results

    def search_by_environment(self, environment: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Busca produtos adequados para um ambiente específico
        
        Args:
            environment: Ambiente (sala, cozinha, banheiro, etc.)
            top_k: Número máximo de resultados
            
        Returns:
            Lista de produtos adequados para o ambiente
        """
        results = []
        env_lower = environment.lower()
        
        for idx, item in enumerate(self.knowledge_base):
            use_cases = [case.lower() for case in item.get('use_case', [])]
            
            if any(env_lower in case or case in env_lower for case in use_cases):
                result = {
                    'document': item,
                    'similarity_score': 1.0,  # Correspondência exata
                    'index': idx
                }
                results.append(result)
                
                if len(results) >= top_k:
                    break
        
        return results

    def add_knowledge_item(self, item: Dict[str, Any]):
        """
        Adiciona novo item à base de conhecimento
        
        Args:
            item: Dicionário com informações do produto/conhecimento
        """
        self.knowledge_base.append(item)
        self._generate_embeddings()  # Regenerar embeddings

    def update_knowledge_base(self, new_knowledge_base: List[Dict[str, Any]]):
        """
        Atualiza toda a base de conhecimento
        
        Args:
            new_knowledge_base: Nova base de conhecimento
        """
        self.knowledge_base = new_knowledge_base
        self._generate_embeddings()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da base de conhecimento
        
        Returns:
            Dicionário com estatísticas
        """
        if not self.knowledge_base:
            return {"total_items": 0}
        
        # Contar por tipo
        type_counts = {}
        brand_counts = {}
        
        for item in self.knowledge_base:
            item_type = item.get('type', 'Não especificado')
            brand = item.get('brand', 'Não especificado')
            
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        return {
            "total_items": len(self.knowledge_base),
            "types": type_counts,
            "brands": brand_counts,
            "has_embeddings": self.embeddings is not None
        }

# Instância global do sistema de busca
pisos_search_system = PisosSemanticSearch()
