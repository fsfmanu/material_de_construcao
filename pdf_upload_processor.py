"""
Sistema de Upload e Processamento de PDFs
Permite upload de novos catálogos em PDF e processamento automático para base de conhecimento.
"""

import os
import json
import uuid
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
from werkzeug.utils import secure_filename
import PyPDF2
from pdfminer.high_level import extract_text
import spacy
import re

class PDFUploadProcessor:
    def __init__(self, upload_folder: str = "/home/ubuntu/agente-tintas/uploads"):
        """
        Inicializa o processador de upload de PDFs
        
        Args:
            upload_folder: Diretório para armazenar uploads
        """
        self.upload_folder = upload_folder
        self.processed_folder = os.path.join(upload_folder, "processed")
        self.temp_folder = os.path.join(upload_folder, "temp")
        
        # Criar diretórios se não existirem
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.processed_folder, exist_ok=True)
        os.makedirs(self.temp_folder, exist_ok=True)
        
        # Extensões permitidas
        self.allowed_extensions = {'pdf'}
        
        # Carregar modelo spaCy para português
        try:
            self.nlp = spacy.load("pt_core_news_sm")
        except OSError:
            print("⚠️  Modelo spaCy não encontrado. Funcionalidade de PLN limitada.")
            self.nlp = None
        
        # Histórico de processamentos
        self.processing_history = []

    def allowed_file(self, filename: str) -> bool:
        """
        Verifica se o arquivo tem extensão permitida
        
        Args:
            filename: Nome do arquivo
            
        Returns:
            True se permitido, False caso contrário
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_uploaded_file(self, file, agent_type: str = "general") -> Dict[str, Any]:
        """
        Salva arquivo enviado pelo usuário
        
        Args:
            file: Arquivo enviado (Flask file object)
            agent_type: Tipo do agente (tintas, pisos, etc.)
            
        Returns:
            Informações do arquivo salvo
        """
        if not file or not file.filename:
            raise ValueError("Nenhum arquivo fornecido")
        
        if not self.allowed_file(file.filename):
            raise ValueError("Tipo de arquivo não permitido. Apenas PDFs são aceitos.")
        
        # Gerar nome único para o arquivo
        file_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        filename = f"{file_id}_{original_filename}"
        
        # Salvar arquivo
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        
        # Informações do arquivo
        file_info = {
            "file_id": file_id,
            "original_filename": original_filename,
            "filename": filename,
            "file_path": file_path,
            "agent_type": agent_type,
            "upload_timestamp": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path),
            "status": "uploaded",
            "processing_status": "pending"
        }
        
        return file_info

    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extrai texto de arquivo PDF
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído
        """
        try:
            # Tentar com pdfminer primeiro (melhor qualidade)
            text = extract_text(file_path)
            if text and len(text.strip()) > 100:
                return text
        except Exception as e:
            print(f"⚠️  Erro com pdfminer: {e}")
        
        try:
            # Fallback para PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"⚠️  Erro com PyPDF2: {e}")
            return ""

    def clean_extracted_text(self, text: str) -> str:
        """
        Limpa e normaliza texto extraído
        
        Args:
            text: Texto bruto extraído
            
        Returns:
            Texto limpo
        """
        if not text:
            return ""
        
        # Remover caracteres especiais e normalizar espaços
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\-.,;:()%°/]', '', text, flags=re.UNICODE)
        
        # Remover linhas muito curtas (provavelmente ruído)
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(cleaned_lines)

    def extract_product_information(self, text: str, agent_type: str) -> List[Dict[str, Any]]:
        """
        Extrai informações de produtos do texto
        
        Args:
            text: Texto do PDF
            agent_type: Tipo do agente (tintas, pisos, etc.)
            
        Returns:
            Lista de produtos extraídos
        """
        products = []
        
        if agent_type == "tintas":
            products = self._extract_paint_products(text)
        elif agent_type == "pisos":
            products = self._extract_floor_products(text)
        else:
            products = self._extract_generic_products(text)
        
        return products

    def _extract_paint_products(self, text: str) -> List[Dict[str, Any]]:
        """Extrai produtos de tinta do texto"""
        products = []
        
        # Padrões para tintas
        paint_patterns = {
            "product_name": r"(?:tinta|verniz|esmalte|primer)\s+([A-Za-z\s\-]+)",
            "brand": r"(?:marca|fabricante):\s*([A-Za-z\s]+)",
            "coverage": r"(?:rendimento|cobertura):\s*(\d+(?:,\d+)?)\s*m²/l",
            "drying_time": r"(?:secagem|seca):\s*(\d+(?:,\d+)?)\s*(?:horas?|h)",
            "dilution": r"(?:diluição|diluir):\s*(\d+(?:,\d+)?%?)",
            "colors": r"(?:cores?|tonalidades?):\s*([A-Za-z\s,]+)"
        }
        
        # Dividir texto em seções (assumindo que cada produto é uma seção)
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            if len(section.strip()) < 50:
                continue
            
            product = {
                "id": str(uuid.uuid4()),
                "type": "tinta",
                "category": "Produto de Pintura",
                "extracted_from": "pdf_upload"
            }
            
            # Extrair informações usando padrões
            for field, pattern in paint_patterns.items():
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    product[field] = match.group(1).strip()
            
            # Extrair características gerais
            features = []
            if "lavável" in section.lower():
                features.append("Lavável")
            if "antimanchas" in section.lower():
                features.append("Antimanchas")
            if "antibactérias" in section.lower():
                features.append("Antibactérias")
            
            product["features"] = features
            product["description"] = section[:200] + "..." if len(section) > 200 else section
            
            if product.get("product_name"):
                products.append(product)
        
        return products

    def _extract_floor_products(self, text: str) -> List[Dict[str, Any]]:
        """Extrai produtos de piso do texto"""
        products = []
        
        # Padrões para pisos
        floor_patterns = {
            "product_name": r"(?:piso|porcelanato|cerâmica|laminado|vinílico)\s+([A-Za-z\s\-]+)",
            "brand": r"(?:marca|fabricante):\s*([A-Za-z\s]+)",
            "size": r"(?:formato|tamanho|dimensão):\s*(\d+x\d+(?:x\d+)?)\s*cm",
            "pei_class": r"PEI\s*(\d)",
            "slip_resistance": r"R(\d+)",
            "water_absorption": r"(?:absorção|absorve):\s*([<>]?\s*\d+(?:,\d+)?%?)",
            "thickness": r"(?:espessura):\s*(\d+(?:,\d+)?)\s*mm"
        }
        
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            if len(section.strip()) < 50:
                continue
            
            product = {
                "id": str(uuid.uuid4()),
                "type": "piso",
                "category": "Revestimento",
                "extracted_from": "pdf_upload"
            }
            
            # Extrair informações usando padrões
            for field, pattern in floor_patterns.items():
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    product[field] = match.group(1).strip()
            
            # Extrair características
            features = []
            if "antiderrapante" in section.lower():
                features.append("Antiderrapante")
            if "retificado" in section.lower():
                features.append("Retificado")
            if "polido" in section.lower():
                features.append("Polido")
            if "acetinado" in section.lower():
                features.append("Acetinado")
            
            product["features"] = features
            product["description"] = section[:200] + "..." if len(section) > 200 else section
            
            if product.get("product_name"):
                products.append(product)
        
        return products

    def _extract_generic_products(self, text: str) -> List[Dict[str, Any]]:
        """Extrai produtos genéricos do texto"""
        products = []
        
        # Implementação básica para produtos genéricos
        sections = re.split(r'\n\s*\n', text)
        
        for section in sections:
            if len(section.strip()) < 50:
                continue
            
            product = {
                "id": str(uuid.uuid4()),
                "type": "generic",
                "category": "Produto",
                "extracted_from": "pdf_upload",
                "description": section[:200] + "..." if len(section) > 200 else section,
                "features": []
            }
            
            products.append(product)
        
        return products

    def process_uploaded_pdf(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa PDF enviado e extrai informações
        
        Args:
            file_info: Informações do arquivo enviado
            
        Returns:
            Resultado do processamento
        """
        try:
            file_path = file_info["file_path"]
            agent_type = file_info.get("agent_type", "general")
            
            # 1. Extrair texto
            print(f"📄 Extraindo texto de {file_info['original_filename']}...")
            raw_text = self.extract_text_from_pdf(file_path)
            
            if not raw_text or len(raw_text.strip()) < 100:
                raise ValueError("Não foi possível extrair texto suficiente do PDF")
            
            # 2. Limpar texto
            print("🧹 Limpando texto extraído...")
            cleaned_text = self.clean_extracted_text(raw_text)
            
            # 3. Extrair produtos
            print("🔍 Extraindo informações de produtos...")
            products = self.extract_product_information(cleaned_text, agent_type)
            
            # 4. Salvar texto processado
            text_filename = f"{file_info['file_id']}_processed.txt"
            text_path = os.path.join(self.processed_folder, text_filename)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # 5. Salvar produtos extraídos
            products_filename = f"{file_info['file_id']}_products.json"
            products_path = os.path.join(self.processed_folder, products_filename)
            with open(products_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            # 6. Resultado do processamento
            processing_result = {
                "file_id": file_info["file_id"],
                "status": "success",
                "processing_timestamp": datetime.now().isoformat(),
                "text_length": len(cleaned_text),
                "products_extracted": len(products),
                "text_file": text_path,
                "products_file": products_path,
                "products": products[:5],  # Primeiros 5 produtos para preview
                "agent_type": agent_type
            }
            
            # Salvar no histórico
            self.processing_history.append(processing_result)
            
            return processing_result
            
        except Exception as e:
            error_result = {
                "file_id": file_info["file_id"],
                "status": "error",
                "error_message": str(e),
                "processing_timestamp": datetime.now().isoformat()
            }
            
            self.processing_history.append(error_result)
            return error_result

    def get_processing_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna histórico de processamentos
        
        Args:
            limit: Número máximo de registros
            
        Returns:
            Lista de processamentos
        """
        return self.processing_history[-limit:]

    def get_processed_products(self, file_id: str) -> List[Dict[str, Any]]:
        """
        Retorna produtos extraídos de um arquivo específico
        
        Args:
            file_id: ID do arquivo
            
        Returns:
            Lista de produtos
        """
        products_path = os.path.join(self.processed_folder, f"{file_id}_products.json")
        
        try:
            with open(products_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def cleanup_temp_files(self, older_than_hours: int = 24):
        """
        Remove arquivos temporários antigos
        
        Args:
            older_than_hours: Remover arquivos mais antigos que X horas
        """
        import time
        
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        for folder in [self.temp_folder, self.upload_folder]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                    try:
                        os.remove(file_path)
                        print(f"🗑️  Arquivo temporário removido: {filename}")
                    except Exception as e:
                        print(f"⚠️  Erro ao remover {filename}: {e}")

    def get_upload_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de uploads
        
        Returns:
            Estatísticas dos uploads
        """
        total_files = len(os.listdir(self.upload_folder))
        processed_files = len([f for f in os.listdir(self.processed_folder) if f.endswith('.json')])
        
        # Estatísticas por agente
        agent_stats = {}
        for result in self.processing_history:
            agent_type = result.get("agent_type", "unknown")
            if agent_type not in agent_stats:
                agent_stats[agent_type] = {"count": 0, "success": 0, "error": 0}
            
            agent_stats[agent_type]["count"] += 1
            if result.get("status") == "success":
                agent_stats[agent_type]["success"] += 1
            else:
                agent_stats[agent_type]["error"] += 1
        
        return {
            "total_uploads": total_files,
            "processed_files": processed_files,
            "processing_history_count": len(self.processing_history),
            "agent_statistics": agent_stats,
            "upload_folder_size_mb": self._get_folder_size(self.upload_folder),
            "processed_folder_size_mb": self._get_folder_size(self.processed_folder)
        }

    def _get_folder_size(self, folder_path: str) -> float:
        """Calcula tamanho de uma pasta em MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                total_size += os.path.getsize(file_path)
        return round(total_size / (1024 * 1024), 2)

# Instância global do processador
pdf_processor = PDFUploadProcessor()
