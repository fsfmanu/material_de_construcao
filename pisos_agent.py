"""
Agente Especialista em Pisos e Revestimentos
Responsável por fornecer consultoria especializada sobre pisos cerâmicos, porcelanatos,
laminados, vinílicos, madeira e pedras naturais.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

class PisosAgent:
    def __init__(self, knowledge_base_path: str = None):
        """
        Inicializa o agente especialista em pisos e revestimentos
        
        Args:
            knowledge_base_path: Caminho para a base de conhecimento em JSON
        """
        self.agent_type = "pisos"
        self.expertise_areas = [
            "pisos_ceramicos",
            "porcelanatos", 
            "pisos_laminados",
            "pisos_vinilicos",
            "pisos_madeira",
            "pedras_naturais",
            "instalacao",
            "manutencao",
            "especificacoes_tecnicas"
        ]
        
        # Base de conhecimento específica de pisos
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        
        # Marcas principais do mercado brasileiro
        self.major_brands = {
            "porcelanato": ["Portinari", "Biancogres", "Portobello", "Eliane", "Cecrisa"],
            "ceramico": ["Eliane", "Portinari", "Cecrisa", "Incepa", "Cedasa"],
            "laminado": ["Durafloor", "Eucafloor", "Floorest", "Quick Step", "Tarkett"],
            "vinilico": ["Tarkett", "Durafloor", "Armstrong", "Beaulieu", "Ambienta"],
            "madeira": ["Indusparquet", "Cumaru", "Barlinek", "Kahrs", "Pergo"]
        }
        
        # Classificações técnicas
        self.pei_classification = {
            1: {"name": "PEI 1", "traffic": "Muito leve", "use": "Quartos, closets"},
            2: {"name": "PEI 2", "traffic": "Leve", "use": "Quartos, salas sem acesso externo"},
            3: {"name": "PEI 3", "traffic": "Médio", "use": "Todas áreas residenciais exceto cozinha"},
            4: {"name": "PEI 4", "traffic": "Médio a intenso", "use": "Todas áreas residenciais e comerciais leves"},
            5: {"name": "PEI 5", "traffic": "Intenso", "use": "Áreas comerciais e industriais"}
        }
        
        self.slip_resistance = {
            "R9": {"condition": "Áreas secas", "angle": "3-10°"},
            "R10": {"condition": "Áreas úmidas ocasionais", "angle": "10-19°"},
            "R11": {"condition": "Áreas molhadas frequentes", "angle": "19-27°"},
            "R12": {"condition": "Áreas com água e sabão", "angle": "27-35°"},
            "R13": {"condition": "Áreas industriais com óleos", "angle": ">35°"}
        }

    def _load_knowledge_base(self, path: str) -> Dict[str, Any]:
        """Carrega a base de conhecimento de pisos"""
        if not path:
            return {}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Base de conhecimento não encontrada: {path}")
            return {}
        except json.JSONDecodeError:
            print(f"⚠️  Erro ao decodificar JSON: {path}")
            return {}

    def identify_floor_type(self, query: str) -> List[str]:
        """
        Identifica o tipo de piso mencionado na consulta
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Lista de tipos de piso identificados
        """
        query_lower = query.lower()
        identified_types = []
        
        # Mapeamento de palavras-chave para tipos de piso
        floor_keywords = {
            "ceramico": ["cerâmic", "azulejo", "revestimento cerâmic"],
            "porcelanato": ["porcelanat", "porcelain"],
            "laminado": ["laminad", "madeira laminad", "piso de madeira"],
            "vinilico": ["vinílic", "pvc", "vinyl"],
            "madeira": ["madeira maciça", "taco", "parquet", "assoalho"],
            "pedra": ["mármore", "granito", "pedra", "travertino", "ardósia"],
            "cimento": ["cimento queimad", "concreto", "industrial"]
        }
        
        for floor_type, keywords in floor_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    identified_types.append(floor_type)
                    break
        
        return list(set(identified_types))  # Remove duplicatas

    def identify_environment(self, query: str) -> List[str]:
        """
        Identifica o ambiente mencionado na consulta
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Lista de ambientes identificados
        """
        query_lower = query.lower()
        environments = []
        
        environment_keywords = {
            "cozinha": ["cozinha", "área gourmet"],
            "banheiro": ["banheiro", "lavabo", "box"],
            "sala": ["sala", "living", "estar"],
            "quarto": ["quarto", "dormitório", "suíte"],
            "area_externa": ["área externa", "varanda", "terraço", "quintal", "piscina"],
            "comercial": ["loja", "escritório", "comercial", "empresa"],
            "industrial": ["indústria", "fábrica", "galpão"]
        }
        
        for env_type, keywords in environment_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    environments.append(env_type)
                    break
        
        return list(set(environments))

    def get_technical_recommendation(self, floor_type: str, environment: str) -> Dict[str, Any]:
        """
        Fornece recomendação técnica baseada no tipo de piso e ambiente
        
        Args:
            floor_type: Tipo de piso
            environment: Ambiente de aplicação
            
        Returns:
            Dicionário com recomendações técnicas
        """
        recommendations = {
            "pei_class": None,
            "slip_resistance": None,
            "water_absorption": None,
            "installation_tips": [],
            "maintenance_tips": []
        }
        
        # Recomendações por ambiente
        if environment in ["cozinha", "banheiro"]:
            recommendations["pei_class"] = 4
            recommendations["slip_resistance"] = "R10"
            recommendations["water_absorption"] = "Baixa (<3%)"
            recommendations["installation_tips"].extend([
                "Use rejunte impermeável",
                "Aplique impermeabilizante antes da instalação",
                "Considere rodapé impermeável"
            ])
        
        elif environment == "area_externa":
            recommendations["pei_class"] = 5
            recommendations["slip_resistance"] = "R11"
            recommendations["water_absorption"] = "Muito baixa (<0.5%)"
            recommendations["installation_tips"].extend([
                "Use argamassa flexível",
                "Considere juntas de dilatação",
                "Verifique resistência ao gelo (se aplicável)"
            ])
        
        elif environment in ["sala", "quarto"]:
            recommendations["pei_class"] = 3
            recommendations["slip_resistance"] = "R9"
            recommendations["installation_tips"].extend([
                "Nivele bem o contrapiso",
                "Use primer se necessário"
            ])
        
        # Recomendações por tipo de piso
        if floor_type == "laminado":
            recommendations["maintenance_tips"].extend([
                "Evite água em excesso",
                "Use produtos específicos para laminado",
                "Aspire regularmente para evitar riscos"
            ])
        
        elif floor_type == "vinilico":
            recommendations["maintenance_tips"].extend([
                "Limpeza diária com pano úmido",
                "Evite produtos abrasivos",
                "Proteja de objetos pontiagudos"
            ])
        
        return recommendations

    def calculate_material_quantity(self, area: float, floor_type: str, 
                                  wastage_factor: float = 0.1) -> Dict[str, Any]:
        """
        Calcula quantidade de material necessária
        
        Args:
            area: Área em m²
            floor_type: Tipo de piso
            wastage_factor: Fator de perda (padrão 10%)
            
        Returns:
            Dicionário com cálculos de material
        """
        # Fatores de perda por tipo de piso
        wastage_factors = {
            "ceramico": 0.10,
            "porcelanato": 0.08,
            "laminado": 0.05,
            "vinilico": 0.05,
            "madeira": 0.15,
            "pedra": 0.15
        }
        
        actual_wastage = wastage_factors.get(floor_type, wastage_factor)
        total_area = area * (1 + actual_wastage)
        
        # Estimativas de materiais complementares
        grout_kg = area * 0.5  # 500g por m² (estimativa)
        adhesive_kg = area * 1.5  # 1.5kg por m² (estimativa)
        
        return {
            "area_liquida": area,
            "fator_perda": actual_wastage,
            "area_total": round(total_area, 2),
            "rejunte_kg": round(grout_kg, 1),
            "argamassa_kg": round(adhesive_kg, 1),
            "observacoes": [
                f"Área líquida: {area}m²",
                f"Fator de perda aplicado: {actual_wastage*100}%",
                f"Área total com perdas: {total_area:.2f}m²"
            ]
        }

    def diagnose_problem(self, problem_description: str) -> Dict[str, Any]:
        """
        Diagnostica problemas comuns em pisos
        
        Args:
            problem_description: Descrição do problema
            
        Returns:
            Diagnóstico e soluções
        """
        problem_lower = problem_description.lower()
        diagnosis = {
            "problema_identificado": "",
            "causas_provaveis": [],
            "solucoes": [],
            "prevencao": []
        }
        
        # Problemas comuns e soluções
        if any(word in problem_lower for word in ["trinca", "rachadura", "fissura"]):
            diagnosis.update({
                "problema_identificado": "Trincas ou rachaduras no piso",
                "causas_provaveis": [
                    "Movimentação da estrutura",
                    "Dilatação térmica inadequada",
                    "Contrapiso mal executado",
                    "Sobrecarga excessiva"
                ],
                "solucoes": [
                    "Avaliar estrutura do imóvel",
                    "Refazer juntas de dilatação",
                    "Substituir peças danificadas",
                    "Reforçar contrapiso se necessário"
                ],
                "prevencao": [
                    "Executar juntas de dilatação adequadas",
                    "Usar argamassa flexível",
                    "Respeitar tempo de cura do contrapiso"
                ]
            })
        
        elif any(word in problem_lower for word in ["mancha", "manchado"]):
            diagnosis.update({
                "problema_identificado": "Manchas no piso",
                "causas_provaveis": [
                    "Porosidade do material",
                    "Falta de impermeabilização",
                    "Produtos de limpeza inadequados",
                    "Infiltração de umidade"
                ],
                "solucoes": [
                    "Limpeza com produtos específicos",
                    "Aplicar impermeabilizante",
                    "Polimento (para pedras naturais)",
                    "Substituição em casos extremos"
                ],
                "prevencao": [
                    "Impermeabilizar superfícies porosas",
                    "Limpeza imediata de respingos",
                    "Usar produtos de limpeza neutros"
                ]
            })
        
        elif any(word in problem_lower for word in ["escorregadio", "escorrega", "derrapante"]):
            diagnosis.update({
                "problema_identificado": "Piso escorregadio",
                "causas_provaveis": [
                    "Acabamento muito liso",
                    "Acúmulo de produtos de limpeza",
                    "Umidade excessiva",
                    "Tipo de piso inadequado para o ambiente"
                ],
                "solucoes": [
                    "Aplicar antiderrapante",
                    "Trocar por piso com maior resistência ao escorregamento",
                    "Melhorar ventilação do ambiente",
                    "Usar tapetes antiderrapantes"
                ],
                "prevencao": [
                    "Escolher piso com classificação R adequada",
                    "Manter ambiente bem ventilado",
                    "Evitar excesso de produtos de limpeza"
                ]
            })
        
        return diagnosis

    def generate_response(self, user_query: str, search_results: List[Dict] = None) -> str:
        """
        Gera resposta especializada em pisos e revestimentos
        
        Args:
            user_query: Consulta do usuário
            search_results: Resultados da busca semântica (opcional)
            
        Returns:
            Resposta formatada do especialista
        """
        query_lower = user_query.lower()
        
        # Identificar contexto da consulta
        floor_types = self.identify_floor_type(user_query)
        environments = self.identify_environment(user_query)
        
        # Resposta base
        response = "Olá! Sou seu especialista em pisos e revestimentos com mais de 15 anos de experiência no mercado. "
        
        # Consultas sobre tipos de piso
        if floor_types:
            response += f"Identifiquei que você está interessado em **{', '.join(floor_types)}**. "
            
            if environments:
                env_text = ', '.join(environments)
                response += f"Para aplicação em **{env_text}**, "
                
                # Recomendação técnica específica
                for floor_type in floor_types:
                    for environment in environments:
                        tech_rec = self.get_technical_recommendation(floor_type, environment)
                        if tech_rec["pei_class"]:
                            response += f"recomendo produtos com classificação **PEI {tech_rec['pei_class']}** "
                        if tech_rec["slip_resistance"]:
                            response += f"e resistência ao escorregamento **{tech_rec['slip_resistance']}**. "
        
        # Consultas sobre problemas
        elif any(word in query_lower for word in ["problema", "trinca", "mancha", "escorrega"]):
            diagnosis = self.diagnose_problem(user_query)
            if diagnosis["problema_identificado"]:
                response += f"Identifiquei o problema: **{diagnosis['problema_identificado']}**.\n\n"
                response += "**Principais causas:**\n"
                for causa in diagnosis["causas_provaveis"][:3]:
                    response += f"• {causa}\n"
                response += "\n**Soluções recomendadas:**\n"
                for solucao in diagnosis["solucoes"][:3]:
                    response += f"• {solucao}\n"
        
        # Consultas sobre cálculo
        elif any(word in query_lower for word in ["calcul", "quantidade", "material"]):
            response += "Para calcular a quantidade correta de material, preciso saber:\n\n"
            response += "📐 **Área total a ser revestida (m²)**\n"
            response += "🏠 **Tipo de ambiente** (sala, cozinha, banheiro, etc.)\n"
            response += "🎯 **Tipo de piso desejado**\n"
            response += "📋 **Formato das peças** (se já definido)\n\n"
            response += "Com essas informações, posso calcular exatamente a quantidade necessária, "
            response += "incluindo o fator de perda adequado para cada tipo de material."
        
        # Consultas sobre instalação
        elif any(word in query_lower for word in ["instala", "como instalar", "aplicar"]):
            response += "A instalação adequada é fundamental para a durabilidade do piso. "
            response += "Os principais passos incluem:\n\n"
            response += "1️⃣ **Preparação do contrapiso** - nivelamento e limpeza\n"
            response += "2️⃣ **Aplicação de primer** (quando necessário)\n"
            response += "3️⃣ **Marcação e planejamento** da paginação\n"
            response += "4️⃣ **Aplicação da argamassa** colante\n"
            response += "5️⃣ **Assentamento das peças** com espaçadores\n"
            response += "6️⃣ **Rejuntamento** após cura da argamassa\n\n"
            response += "Cada tipo de piso tem suas particularidades. Qual tipo você pretende instalar?"
        
        # Resposta genérica com opções
        else:
            response += "Posso ajudá-lo com:\n\n"
            response += "🎯 **Escolha do piso ideal** para cada ambiente\n"
            response += "📊 **Cálculo de materiais** e quantidades\n"
            response += "🔧 **Orientações de instalação** e manutenção\n"
            response += "🏥 **Diagnóstico de problemas** em pisos existentes\n"
            response += "💡 **Recomendações técnicas** (PEI, resistência, etc.)\n"
            response += "🏭 **Indicação de marcas** e fornecedores\n\n"
            response += "Qual sua necessidade específica?"
        
        # Adicionar informações dos resultados da busca se disponível
        if search_results:
            response += "\n\n**Produtos relacionados encontrados:**\n"
            for i, result in enumerate(search_results[:2], 1):
                doc = result.get('document', {})
                response += f"{i}. **{doc.get('product_name', 'Produto')}** - {doc.get('brand', 'Marca')}\n"
                if doc.get('features'):
                    response += f"   Características: {', '.join(doc.get('features', [])[:2])}\n"
        
        return response

    def get_brand_info(self, floor_type: str) -> List[str]:
        """
        Retorna informações sobre marcas principais por tipo de piso
        
        Args:
            floor_type: Tipo de piso
            
        Returns:
            Lista de marcas principais
        """
        return self.major_brands.get(floor_type, [])

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Retorna informações do agente
        
        Returns:
            Dicionário com informações do agente
        """
        return {
            "agent_type": self.agent_type,
            "name": "Agente Especialista em Pisos e Revestimentos",
            "expertise_areas": self.expertise_areas,
            "major_brands": self.major_brands,
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat()
        }

# Instância global do agente
pisos_agent = PisosAgent()
