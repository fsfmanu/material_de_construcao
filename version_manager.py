"""
Sistema de Versionamento para Prompts e Conhecimento
Permite controle de versões, histórico de alterações e rollback.
"""

import json
import uuid
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, asdict
import copy
import hashlib

@dataclass
class Version:
    """Representa uma versão de um item"""
    id: str
    item_id: str
    item_type: str  # 'prompt' ou 'knowledge'
    version_number: int
    content: Dict[str, Any]
    changes_summary: str
    created_by: str
    created_at: str
    tags: List[str]
    is_current: bool
    parent_version_id: Optional[str] = None

@dataclass
class ChangeLog:
    """Representa um log de mudança"""
    id: str
    item_id: str
    version_id: str
    action: str  # 'create', 'update', 'delete', 'rollback'
    changes: Dict[str, Any]
    user: str
    timestamp: str
    description: str

class VersionManager:
    def __init__(self):
        """
        Inicializa o gerenciador de versões
        """
        self.versions = {}  # {item_id: [versions]}
        self.change_logs = []
        self.version_counter = {}  # {item_id: current_version_number}

    def create_version(self, 
                      item_id: str,
                      item_type: str,
                      content: Dict[str, Any],
                      changes_summary: str = "Versão inicial",
                      created_by: str = "system",
                      tags: List[str] = None,
                      parent_version_id: str = None) -> Version:
        """
        Cria uma nova versão de um item
        
        Args:
            item_id: ID do item
            item_type: Tipo do item ('prompt' ou 'knowledge')
            content: Conteúdo da versão
            changes_summary: Resumo das mudanças
            created_by: Usuário que criou a versão
            tags: Tags da versão
            parent_version_id: ID da versão pai
            
        Returns:
            Versão criada
        """
        version_id = str(uuid.uuid4())
        
        # Determinar número da versão
        if item_id not in self.version_counter:
            self.version_counter[item_id] = 0
        
        self.version_counter[item_id] += 1
        version_number = self.version_counter[item_id]
        
        # Marcar versões anteriores como não atuais
        if item_id in self.versions:
            for version in self.versions[item_id]:
                version.is_current = False
        
        # Criar nova versão
        version = Version(
            id=version_id,
            item_id=item_id,
            item_type=item_type,
            version_number=version_number,
            content=copy.deepcopy(content),
            changes_summary=changes_summary,
            created_by=created_by,
            created_at=datetime.now().isoformat(),
            tags=tags or [],
            is_current=True,
            parent_version_id=parent_version_id
        )
        
        # Adicionar à lista de versões
        if item_id not in self.versions:
            self.versions[item_id] = []
        
        self.versions[item_id].append(version)
        
        # Criar log de mudança
        self._create_change_log(
            item_id=item_id,
            version_id=version_id,
            action="create" if version_number == 1 else "update",
            changes=self._calculate_changes(item_id, content),
            user=created_by,
            description=changes_summary
        )
        
        return version

    def get_current_version(self, item_id: str) -> Optional[Version]:
        """
        Retorna a versão atual de um item
        
        Args:
            item_id: ID do item
            
        Returns:
            Versão atual ou None se não encontrada
        """
        if item_id not in self.versions:
            return None
        
        for version in self.versions[item_id]:
            if version.is_current:
                return version
        
        return None

    def get_version_by_id(self, version_id: str) -> Optional[Version]:
        """
        Retorna uma versão específica pelo ID
        
        Args:
            version_id: ID da versão
            
        Returns:
            Versão encontrada ou None
        """
        for item_id in self.versions:
            for version in self.versions[item_id]:
                if version.id == version_id:
                    return version
        
        return None

    def get_version_history(self, item_id: str, limit: int = 50) -> List[Version]:
        """
        Retorna histórico de versões de um item
        
        Args:
            item_id: ID do item
            limit: Número máximo de versões
            
        Returns:
            Lista de versões ordenadas por data (mais recente primeiro)
        """
        if item_id not in self.versions:
            return []
        
        versions = sorted(
            self.versions[item_id],
            key=lambda v: v.created_at,
            reverse=True
        )
        
        return versions[:limit]

    def rollback_to_version(self, 
                           item_id: str,
                           target_version_id: str,
                           rollback_by: str = "system",
                           rollback_reason: str = "Rollback solicitado") -> Optional[Version]:
        """
        Faz rollback para uma versão específica
        
        Args:
            item_id: ID do item
            target_version_id: ID da versão alvo
            rollback_by: Usuário que solicitou o rollback
            rollback_reason: Motivo do rollback
            
        Returns:
            Nova versão criada com o conteúdo da versão alvo
        """
        target_version = self.get_version_by_id(target_version_id)
        
        if not target_version or target_version.item_id != item_id:
            return None
        
        # Criar nova versão com o conteúdo da versão alvo
        new_version = self.create_version(
            item_id=item_id,
            item_type=target_version.item_type,
            content=target_version.content,
            changes_summary=f"Rollback para versão {target_version.version_number}: {rollback_reason}",
            created_by=rollback_by,
            tags=["rollback"] + target_version.tags,
            parent_version_id=target_version.id
        )
        
        # Criar log específico de rollback
        self._create_change_log(
            item_id=item_id,
            version_id=new_version.id,
            action="rollback",
            changes={
                "target_version": target_version_id,
                "target_version_number": target_version.version_number
            },
            user=rollback_by,
            description=rollback_reason
        )
        
        return new_version

    def compare_versions(self, version_id_1: str, version_id_2: str) -> Dict[str, Any]:
        """
        Compara duas versões
        
        Args:
            version_id_1: ID da primeira versão
            version_id_2: ID da segunda versão
            
        Returns:
            Resultado da comparação
        """
        version_1 = self.get_version_by_id(version_id_1)
        version_2 = self.get_version_by_id(version_id_2)
        
        if not version_1 or not version_2:
            return {"error": "Uma ou ambas as versões não foram encontradas"}
        
        if version_1.item_id != version_2.item_id:
            return {"error": "As versões pertencem a itens diferentes"}
        
        # Comparar conteúdos
        differences = self._deep_compare(version_1.content, version_2.content)
        
        return {
            "version_1": {
                "id": version_1.id,
                "version_number": version_1.version_number,
                "created_at": version_1.created_at,
                "created_by": version_1.created_by
            },
            "version_2": {
                "id": version_2.id,
                "version_number": version_2.version_number,
                "created_at": version_2.created_at,
                "created_by": version_2.created_by
            },
            "differences": differences,
            "has_changes": len(differences) > 0
        }

    def get_change_logs(self, 
                       item_id: str = None,
                       user: str = None,
                       action: str = None,
                       limit: int = 100) -> List[ChangeLog]:
        """
        Retorna logs de mudanças com filtros opcionais
        
        Args:
            item_id: Filtrar por item (opcional)
            user: Filtrar por usuário (opcional)
            action: Filtrar por ação (opcional)
            limit: Número máximo de logs
            
        Returns:
            Lista de logs de mudança
        """
        filtered_logs = []
        
        for log in self.change_logs:
            # Aplicar filtros
            if item_id and log.item_id != item_id:
                continue
            if user and log.user != user:
                continue
            if action and log.action != action:
                continue
            
            filtered_logs.append(log)
        
        # Ordenar por timestamp (mais recente primeiro)
        filtered_logs.sort(key=lambda l: l.timestamp, reverse=True)
        
        return filtered_logs[:limit]

    def create_branch(self, 
                     base_version_id: str,
                     branch_name: str,
                     created_by: str = "system") -> Optional[Version]:
        """
        Cria uma branch (ramificação) a partir de uma versão
        
        Args:
            base_version_id: ID da versão base
            branch_name: Nome da branch
            created_by: Usuário que criou a branch
            
        Returns:
            Nova versão da branch
        """
        base_version = self.get_version_by_id(base_version_id)
        
        if not base_version:
            return None
        
        # Criar nova versão como branch
        branch_version = self.create_version(
            item_id=f"{base_version.item_id}_branch_{branch_name}",
            item_type=base_version.item_type,
            content=base_version.content,
            changes_summary=f"Branch '{branch_name}' criada a partir da versão {base_version.version_number}",
            created_by=created_by,
            tags=["branch", branch_name] + base_version.tags,
            parent_version_id=base_version_id
        )
        
        return branch_version

    def merge_branch(self, 
                    main_item_id: str,
                    branch_item_id: str,
                    merge_by: str = "system",
                    merge_strategy: str = "overwrite") -> Optional[Version]:
        """
        Faz merge de uma branch com o item principal
        
        Args:
            main_item_id: ID do item principal
            branch_item_id: ID da branch
            merge_by: Usuário que fez o merge
            merge_strategy: Estratégia de merge ('overwrite', 'merge')
            
        Returns:
            Nova versão com o merge
        """
        main_version = self.get_current_version(main_item_id)
        branch_version = self.get_current_version(branch_item_id)
        
        if not main_version or not branch_version:
            return None
        
        # Aplicar estratégia de merge
        if merge_strategy == "overwrite":
            merged_content = copy.deepcopy(branch_version.content)
        elif merge_strategy == "merge":
            merged_content = self._merge_content(main_version.content, branch_version.content)
        else:
            return None
        
        # Criar nova versão com o merge
        merged_version = self.create_version(
            item_id=main_item_id,
            item_type=main_version.item_type,
            content=merged_content,
            changes_summary=f"Merge da branch {branch_item_id} usando estratégia '{merge_strategy}'",
            created_by=merge_by,
            tags=["merge"] + main_version.tags + branch_version.tags,
            parent_version_id=main_version.id
        )
        
        return merged_version

    def tag_version(self, version_id: str, tags: List[str]) -> bool:
        """
        Adiciona tags a uma versão
        
        Args:
            version_id: ID da versão
            tags: Lista de tags para adicionar
            
        Returns:
            True se sucesso, False se versão não encontrada
        """
        version = self.get_version_by_id(version_id)
        
        if not version:
            return False
        
        # Adicionar tags únicas
        for tag in tags:
            if tag not in version.tags:
                version.tags.append(tag)
        
        return True

    def get_versions_by_tag(self, tag: str) -> List[Version]:
        """
        Retorna versões que possuem uma tag específica
        
        Args:
            tag: Tag para buscar
            
        Returns:
            Lista de versões com a tag
        """
        tagged_versions = []
        
        for item_id in self.versions:
            for version in self.versions[item_id]:
                if tag in version.tags:
                    tagged_versions.append(version)
        
        return tagged_versions

    def get_version_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de versionamento
        
        Returns:
            Estatísticas detalhadas
        """
        total_items = len(self.versions)
        total_versions = sum(len(versions) for versions in self.versions.values())
        
        # Estatísticas por tipo
        type_stats = {}
        for item_id in self.versions:
            for version in self.versions[item_id]:
                item_type = version.item_type
                if item_type not in type_stats:
                    type_stats[item_type] = {"items": set(), "versions": 0}
                
                type_stats[item_type]["items"].add(item_id)
                type_stats[item_type]["versions"] += 1
        
        # Converter sets para contadores
        for item_type in type_stats:
            type_stats[item_type]["items"] = len(type_stats[item_type]["items"])
        
        # Estatísticas de ações
        action_stats = {}
        for log in self.change_logs:
            action = log.action
            action_stats[action] = action_stats.get(action, 0) + 1
        
        # Usuários mais ativos
        user_stats = {}
        for log in self.change_logs:
            user = log.user
            user_stats[user] = user_stats.get(user, 0) + 1
        
        return {
            "total_items": total_items,
            "total_versions": total_versions,
            "total_change_logs": len(self.change_logs),
            "average_versions_per_item": round(total_versions / total_items, 2) if total_items > 0 else 0,
            "type_statistics": type_stats,
            "action_statistics": action_stats,
            "user_statistics": dict(sorted(user_stats.items(), key=lambda x: x[1], reverse=True)[:10])
        }

    def _create_change_log(self, 
                          item_id: str,
                          version_id: str,
                          action: str,
                          changes: Dict[str, Any],
                          user: str,
                          description: str):
        """Cria um log de mudança"""
        log = ChangeLog(
            id=str(uuid.uuid4()),
            item_id=item_id,
            version_id=version_id,
            action=action,
            changes=changes,
            user=user,
            timestamp=datetime.now().isoformat(),
            description=description
        )
        
        self.change_logs.append(log)

    def _calculate_changes(self, item_id: str, new_content: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula mudanças entre versões"""
        if item_id not in self.versions or len(self.versions[item_id]) == 0:
            return {"type": "initial_creation"}
        
        # Pegar versão anterior
        previous_versions = [v for v in self.versions[item_id] if not v.is_current]
        if not previous_versions:
            return {"type": "initial_creation"}
        
        previous_version = max(previous_versions, key=lambda v: v.version_number)
        
        return self._deep_compare(previous_version.content, new_content)

    def _deep_compare(self, obj1: Any, obj2: Any, path: str = "") -> Dict[str, Any]:
        """Compara profundamente dois objetos"""
        changes = {}
        
        if type(obj1) != type(obj2):
            changes[path or "root"] = {
                "type": "type_change",
                "old_type": type(obj1).__name__,
                "new_type": type(obj2).__name__,
                "old_value": obj1,
                "new_value": obj2
            }
            return changes
        
        if isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            
            for key in all_keys:
                key_path = f"{path}.{key}" if path else key
                
                if key not in obj1:
                    changes[key_path] = {
                        "type": "added",
                        "value": obj2[key]
                    }
                elif key not in obj2:
                    changes[key_path] = {
                        "type": "removed",
                        "value": obj1[key]
                    }
                elif obj1[key] != obj2[key]:
                    nested_changes = self._deep_compare(obj1[key], obj2[key], key_path)
                    changes.update(nested_changes)
        
        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                changes[path or "root"] = {
                    "type": "list_length_change",
                    "old_length": len(obj1),
                    "new_length": len(obj2),
                    "old_value": obj1,
                    "new_value": obj2
                }
            else:
                for i, (item1, item2) in enumerate(zip(obj1, obj2)):
                    if item1 != item2:
                        item_path = f"{path}[{i}]" if path else f"[{i}]"
                        nested_changes = self._deep_compare(item1, item2, item_path)
                        changes.update(nested_changes)
        
        else:
            if obj1 != obj2:
                changes[path or "root"] = {
                    "type": "value_change",
                    "old_value": obj1,
                    "new_value": obj2
                }
        
        return changes

    def _merge_content(self, main_content: Dict[str, Any], branch_content: Dict[str, Any]) -> Dict[str, Any]:
        """Faz merge inteligente de conteúdos"""
        merged = copy.deepcopy(main_content)
        
        for key, value in branch_content.items():
            if key not in merged:
                # Adicionar nova chave
                merged[key] = value
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                # Merge recursivo para dicionários
                merged[key] = self._merge_content(merged[key], value)
            elif isinstance(merged[key], list) and isinstance(value, list):
                # Combinar listas (removendo duplicatas)
                merged[key] = list(set(merged[key] + value))
            else:
                # Sobrescrever valor
                merged[key] = value
        
        return merged

    def export_versions(self, item_id: str = None) -> str:
        """
        Exporta versões em formato JSON
        
        Args:
            item_id: ID do item (opcional, exporta todos se None)
            
        Returns:
            String JSON com as versões
        """
        if item_id:
            if item_id not in self.versions:
                return json.dumps({"error": "Item não encontrado"})
            
            export_data = {
                "item_id": item_id,
                "versions": [asdict(v) for v in self.versions[item_id]],
                "change_logs": [asdict(log) for log in self.change_logs if log.item_id == item_id]
            }
        else:
            export_data = {
                "all_versions": {
                    item_id: [asdict(v) for v in versions]
                    for item_id, versions in self.versions.items()
                },
                "all_change_logs": [asdict(log) for log in self.change_logs],
                "version_counters": self.version_counter
            }
        
        return json.dumps(export_data, ensure_ascii=False, indent=2)

    def import_versions(self, data: str) -> Dict[str, Any]:
        """
        Importa versões de formato JSON
        
        Args:
            data: String JSON com as versões
            
        Returns:
            Resultado da importação
        """
        try:
            import_data = json.loads(data)
            imported_items = 0
            imported_versions = 0
            imported_logs = 0
            
            if "all_versions" in import_data:
                # Importação completa
                for item_id, versions_data in import_data["all_versions"].items():
                    self.versions[item_id] = []
                    for version_data in versions_data:
                        version = Version(**version_data)
                        self.versions[item_id].append(version)
                        imported_versions += 1
                    imported_items += 1
                
                # Importar logs
                if "all_change_logs" in import_data:
                    for log_data in import_data["all_change_logs"]:
                        log = ChangeLog(**log_data)
                        self.change_logs.append(log)
                        imported_logs += 1
                
                # Importar contadores
                if "version_counters" in import_data:
                    self.version_counter.update(import_data["version_counters"])
            
            else:
                # Importação de item único
                item_id = import_data["item_id"]
                self.versions[item_id] = []
                
                for version_data in import_data["versions"]:
                    version = Version(**version_data)
                    self.versions[item_id].append(version)
                    imported_versions += 1
                
                imported_items = 1
                
                # Importar logs do item
                if "change_logs" in import_data:
                    for log_data in import_data["change_logs"]:
                        log = ChangeLog(**log_data)
                        self.change_logs.append(log)
                        imported_logs += 1
            
            return {
                "success": True,
                "imported_items": imported_items,
                "imported_versions": imported_versions,
                "imported_logs": imported_logs,
                "message": f"Importação concluída: {imported_items} itens, {imported_versions} versões, {imported_logs} logs"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao importar versões"
            }

# Instância global do gerenciador de versões
version_manager = VersionManager()
