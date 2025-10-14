"""
Editor Visual de Base de Conhecimento
Permite edição visual e estruturada da base de conhecimento dos agentes.
"""

import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import copy

@dataclass
class KnowledgeItem:
    """Representa um item de conhecimento estruturado"""
    id: str
    title: str
    content: str
    category: str
    agent_type: str
    tags: List[str]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str
    version: int
    status: str  # active, draft, archived

class KnowledgeEditor:
    def __init__(self):
        """
        Inicializa o editor de base de conhecimento
        """
        self.knowledge_base = {}  # {agent_type: {category: [items]}}
        self.categories = {
            "tintas": [
                "Produtos", "Técnicas de Aplicação", "Problemas e Soluções",
                "Cálculos", "Especificações Técnicas", "Cores e Acabamentos",
                "Ferramentas", "Sustentabilidade", "FAQ"
            ],
            "pisos": [
                "Produtos", "Instalação", "Manutenção", "Especificações Técnicas",
                "Ambientes de Uso", "Problemas e Soluções", "Ferramentas",
                "Normas e Certificações", "FAQ"
            ],
            "geral": [
                "Atendimento", "Políticas", "Procedimentos", "Contato",
                "Horários", "Localização", "FAQ"
            ]
        }
        
        # Templates para diferentes tipos de conhecimento
        self.templates = {
            "produto": {
                "title": "Nome do Produto",
                "content": "Descrição detalhada do produto...",
                "metadata": {
                    "brand": "",
                    "type": "",
                    "features": [],
                    "specifications": {},
                    "use_cases": [],
                    "price_range": "",
                    "availability": "available"
                }
            },
            "tecnica": {
                "title": "Técnica de Aplicação",
                "content": "Passo a passo da técnica...",
                "metadata": {
                    "difficulty": "beginner",
                    "time_required": "",
                    "tools_needed": [],
                    "materials": [],
                    "tips": []
                }
            },
            "problema": {
                "title": "Problema e Solução",
                "content": "Descrição do problema e como resolver...",
                "metadata": {
                    "problem_type": "",
                    "causes": [],
                    "solutions": [],
                    "prevention": [],
                    "severity": "low"
                }
            },
            "faq": {
                "title": "Pergunta Frequente",
                "content": "Resposta detalhada...",
                "metadata": {
                    "question": "",
                    "keywords": [],
                    "related_topics": [],
                    "frequency": "common"
                }
            }
        }

    def create_knowledge_item(self, 
                            title: str,
                            content: str,
                            category: str,
                            agent_type: str,
                            tags: List[str] = None,
                            metadata: Dict[str, Any] = None,
                            template_type: str = None) -> KnowledgeItem:
        """
        Cria um novo item de conhecimento
        
        Args:
            title: Título do item
            content: Conteúdo do item
            category: Categoria do item
            agent_type: Tipo do agente (tintas, pisos, geral)
            tags: Lista de tags
            metadata: Metadados específicos
            template_type: Tipo de template a usar
            
        Returns:
            Item de conhecimento criado
        """
        item_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Aplicar template se especificado
        if template_type and template_type in self.templates:
            template = self.templates[template_type]
            if not title or title == "":
                title = template["title"]
            if not content or content == "":
                content = template["content"]
            if not metadata:
                metadata = copy.deepcopy(template["metadata"])
        
        item = KnowledgeItem(
            id=item_id,
            title=title,
            content=content,
            category=category,
            agent_type=agent_type,
            tags=tags or [],
            metadata=metadata or {},
            created_at=now,
            updated_at=now,
            version=1,
            status="draft"
        )
        
        # Adicionar à base de conhecimento
        if agent_type not in self.knowledge_base:
            self.knowledge_base[agent_type] = {}
        if category not in self.knowledge_base[agent_type]:
            self.knowledge_base[agent_type][category] = []
        
        self.knowledge_base[agent_type][category].append(item)
        
        return item

    def update_knowledge_item(self, 
                            item_id: str,
                            title: str = None,
                            content: str = None,
                            category: str = None,
                            tags: List[str] = None,
                            metadata: Dict[str, Any] = None,
                            status: str = None) -> Optional[KnowledgeItem]:
        """
        Atualiza um item de conhecimento existente
        
        Args:
            item_id: ID do item a atualizar
            title: Novo título (opcional)
            content: Novo conteúdo (opcional)
            category: Nova categoria (opcional)
            tags: Novas tags (opcional)
            metadata: Novos metadados (opcional)
            status: Novo status (opcional)
            
        Returns:
            Item atualizado ou None se não encontrado
        """
        item = self.find_knowledge_item(item_id)
        if not item:
            return None
        
        # Atualizar campos se fornecidos
        if title is not None:
            item.title = title
        if content is not None:
            item.content = content
        if tags is not None:
            item.tags = tags
        if metadata is not None:
            item.metadata.update(metadata)
        if status is not None:
            item.status = status
        
        # Mover para nova categoria se necessário
        if category is not None and category != item.category:
            self.move_item_to_category(item_id, category)
            item.category = category
        
        # Atualizar timestamp e versão
        item.updated_at = datetime.now().isoformat()
        item.version += 1
        
        return item

    def find_knowledge_item(self, item_id: str) -> Optional[KnowledgeItem]:
        """
        Encontra um item de conhecimento pelo ID
        
        Args:
            item_id: ID do item
            
        Returns:
            Item encontrado ou None
        """
        for agent_type in self.knowledge_base:
            for category in self.knowledge_base[agent_type]:
                for item in self.knowledge_base[agent_type][category]:
                    if item.id == item_id:
                        return item
        return None

    def delete_knowledge_item(self, item_id: str) -> bool:
        """
        Remove um item de conhecimento
        
        Args:
            item_id: ID do item a remover
            
        Returns:
            True se removido, False se não encontrado
        """
        for agent_type in self.knowledge_base:
            for category in self.knowledge_base[agent_type]:
                for i, item in enumerate(self.knowledge_base[agent_type][category]):
                    if item.id == item_id:
                        del self.knowledge_base[agent_type][category][i]
                        return True
        return False

    def move_item_to_category(self, item_id: str, new_category: str) -> bool:
        """
        Move um item para uma nova categoria
        
        Args:
            item_id: ID do item
            new_category: Nova categoria
            
        Returns:
            True se movido, False se não encontrado
        """
        item = self.find_knowledge_item(item_id)
        if not item:
            return False
        
        # Remover da categoria atual
        old_category = item.category
        agent_type = item.agent_type
        
        for i, existing_item in enumerate(self.knowledge_base[agent_type][old_category]):
            if existing_item.id == item_id:
                del self.knowledge_base[agent_type][old_category][i]
                break
        
        # Adicionar à nova categoria
        if new_category not in self.knowledge_base[agent_type]:
            self.knowledge_base[agent_type][new_category] = []
        
        item.category = new_category
        self.knowledge_base[agent_type][new_category].append(item)
        
        return True

    def get_knowledge_by_agent(self, agent_type: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna todo o conhecimento de um agente específico
        
        Args:
            agent_type: Tipo do agente
            
        Returns:
            Dicionário com categorias e itens
        """
        if agent_type not in self.knowledge_base:
            return {}
        
        result = {}
        for category, items in self.knowledge_base[agent_type].items():
            result[category] = [asdict(item) for item in items]
        
        return result

    def get_knowledge_by_category(self, agent_type: str, category: str) -> List[Dict[str, Any]]:
        """
        Retorna conhecimento de uma categoria específica
        
        Args:
            agent_type: Tipo do agente
            category: Categoria
            
        Returns:
            Lista de itens da categoria
        """
        if agent_type not in self.knowledge_base or category not in self.knowledge_base[agent_type]:
            return []
        
        return [asdict(item) for item in self.knowledge_base[agent_type][category]]

    def search_knowledge(self, 
                        query: str,
                        agent_type: str = None,
                        category: str = None,
                        tags: List[str] = None,
                        status: str = None) -> List[Dict[str, Any]]:
        """
        Busca itens de conhecimento
        
        Args:
            query: Termo de busca
            agent_type: Filtrar por tipo de agente
            category: Filtrar por categoria
            tags: Filtrar por tags
            status: Filtrar por status
            
        Returns:
            Lista de itens encontrados
        """
        results = []
        query_lower = query.lower() if query else ""
        
        for agent in self.knowledge_base:
            if agent_type and agent != agent_type:
                continue
            
            for cat in self.knowledge_base[agent]:
                if category and cat != category:
                    continue
                
                for item in self.knowledge_base[agent][cat]:
                    # Filtros
                    if status and item.status != status:
                        continue
                    
                    if tags and not any(tag in item.tags for tag in tags):
                        continue
                    
                    # Busca textual
                    if query:
                        searchable_text = f"{item.title} {item.content} {' '.join(item.tags)}".lower()
                        if query_lower not in searchable_text:
                            continue
                    
                    results.append(asdict(item))
        
        return results

    def get_available_categories(self, agent_type: str = None) -> List[str]:
        """
        Retorna categorias disponíveis
        
        Args:
            agent_type: Tipo do agente (opcional)
            
        Returns:
            Lista de categorias
        """
        if agent_type:
            return self.categories.get(agent_type, [])
        
        all_categories = set()
        for categories in self.categories.values():
            all_categories.update(categories)
        
        return sorted(list(all_categories))

    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna templates disponíveis
        
        Returns:
            Dicionário com templates
        """
        return self.templates

    def duplicate_knowledge_item(self, item_id: str, new_title: str = None) -> Optional[KnowledgeItem]:
        """
        Duplica um item de conhecimento
        
        Args:
            item_id: ID do item a duplicar
            new_title: Novo título (opcional)
            
        Returns:
            Item duplicado ou None se não encontrado
        """
        original = self.find_knowledge_item(item_id)
        if not original:
            return None
        
        title = new_title or f"{original.title} (Cópia)"
        
        return self.create_knowledge_item(
            title=title,
            content=original.content,
            category=original.category,
            agent_type=original.agent_type,
            tags=original.tags.copy(),
            metadata=copy.deepcopy(original.metadata)
        )

    def export_knowledge(self, agent_type: str = None, format: str = "json") -> str:
        """
        Exporta base de conhecimento
        
        Args:
            agent_type: Tipo do agente (opcional, exporta todos se None)
            format: Formato de exportação (json)
            
        Returns:
            String com dados exportados
        """
        if agent_type:
            data = self.get_knowledge_by_agent(agent_type)
        else:
            data = {}
            for agent in self.knowledge_base:
                data[agent] = self.get_knowledge_by_agent(agent)
        
        if format == "json":
            return json.dumps(data, ensure_ascii=False, indent=2)
        
        return str(data)

    def import_knowledge(self, data: str, agent_type: str, merge: bool = True) -> Dict[str, Any]:
        """
        Importa base de conhecimento
        
        Args:
            data: Dados em formato JSON
            agent_type: Tipo do agente
            merge: Se True, mescla com existente; se False, substitui
            
        Returns:
            Resultado da importação
        """
        try:
            imported_data = json.loads(data)
            
            if not merge:
                # Limpar conhecimento existente
                self.knowledge_base[agent_type] = {}
            
            imported_count = 0
            
            for category, items in imported_data.items():
                for item_data in items:
                    # Criar novo item
                    item = self.create_knowledge_item(
                        title=item_data.get("title", ""),
                        content=item_data.get("content", ""),
                        category=category,
                        agent_type=agent_type,
                        tags=item_data.get("tags", []),
                        metadata=item_data.get("metadata", {})
                    )
                    
                    # Preservar status se fornecido
                    if "status" in item_data:
                        item.status = item_data["status"]
                    
                    imported_count += 1
            
            return {
                "success": True,
                "imported_count": imported_count,
                "message": f"{imported_count} itens importados com sucesso"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao importar dados"
            }

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas da base de conhecimento
        
        Returns:
            Estatísticas detalhadas
        """
        stats = {
            "total_items": 0,
            "by_agent": {},
            "by_status": {"active": 0, "draft": 0, "archived": 0},
            "by_category": {},
            "recent_updates": []
        }
        
        all_items = []
        
        for agent_type in self.knowledge_base:
            agent_count = 0
            stats["by_agent"][agent_type] = {"total": 0, "by_category": {}}
            
            for category in self.knowledge_base[agent_type]:
                category_count = len(self.knowledge_base[agent_type][category])
                agent_count += category_count
                
                stats["by_agent"][agent_type]["by_category"][category] = category_count
                stats["by_category"][category] = stats["by_category"].get(category, 0) + category_count
                
                # Coletar todos os itens para outras estatísticas
                for item in self.knowledge_base[agent_type][category]:
                    all_items.append(item)
                    stats["by_status"][item.status] = stats["by_status"].get(item.status, 0) + 1
            
            stats["by_agent"][agent_type]["total"] = agent_count
            stats["total_items"] += agent_count
        
        # Itens recentemente atualizados (últimos 10)
        all_items.sort(key=lambda x: x.updated_at, reverse=True)
        stats["recent_updates"] = [
            {
                "id": item.id,
                "title": item.title,
                "agent_type": item.agent_type,
                "category": item.category,
                "updated_at": item.updated_at
            }
            for item in all_items[:10]
        ]
        
        return stats

    def validate_knowledge_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida um item de conhecimento
        
        Args:
            item_data: Dados do item
            
        Returns:
            Resultado da validação
        """
        errors = []
        warnings = []
        
        # Validações obrigatórias
        if not item_data.get("title"):
            errors.append("Título é obrigatório")
        
        if not item_data.get("content"):
            errors.append("Conteúdo é obrigatório")
        
        if not item_data.get("category"):
            errors.append("Categoria é obrigatória")
        
        if not item_data.get("agent_type"):
            errors.append("Tipo de agente é obrigatório")
        
        # Validações de formato
        if item_data.get("title") and len(item_data["title"]) > 200:
            warnings.append("Título muito longo (máximo 200 caracteres)")
        
        if item_data.get("content") and len(item_data["content"]) < 10:
            warnings.append("Conteúdo muito curto (mínimo 10 caracteres)")
        
        # Validar categoria
        agent_type = item_data.get("agent_type")
        category = item_data.get("category")
        if agent_type and category:
            valid_categories = self.categories.get(agent_type, [])
            if category not in valid_categories:
                warnings.append(f"Categoria '{category}' não é padrão para agente '{agent_type}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

# Instância global do editor
knowledge_editor = KnowledgeEditor()
