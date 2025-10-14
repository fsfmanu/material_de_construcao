import json
import os
from datetime import datetime

class ProductManager:
    def __init__(self, products_file='products_catalog.json'):
        self.products_file = products_file
        self.products = self.load_products()
        
    def load_products(self):
        """Carrega produtos do arquivo JSON ou cria catálogo inicial"""
        if os.path.exists(self.products_file):
            with open(self.products_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Criar catálogo inicial simulado
            initial_products = self.create_initial_catalog()
            self.save_products(initial_products)
            return initial_products
    
    def save_products(self, products=None):
        """Salva produtos no arquivo JSON"""
        if products is None:
            products = self.products
        
        with open(self.products_file, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
    
    def create_initial_catalog(self):
        """Cria catálogo inicial com produtos simulados baseados na base de conhecimento"""
        return {
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0",
                "currency": "BRL"
            },
            "products": [
                {
                    "id": "CORAL_001",
                    "name": "Coral Acrílica Premium",
                    "brand": "Coral",
                    "category": "Tinta Acrílica",
                    "type": "Residencial",
                    "description": "Tinta acrílica premium para paredes internas e externas",
                    "coverage": "14 m²/L",
                    "drying_time": "2 horas ao toque, 4 horas entre demãos",
                    "dilution": "Até 20% com água",
                    "application_tools": ["Rolo", "Pincel", "Pistola"],
                    "use_case": ["Internas", "Externas", "Alvenaria", "Gesso", "Drywall"],
                    "features": ["Lavável", "Antimofo", "Sem cheiro", "Cobertura superior"],
                    "colors": ["Branco", "Cores diversas"],
                    "packages": [
                        {"size": "3.6L", "price": 89.90, "stock": 25},
                        {"size": "18L", "price": 389.90, "stock": 15}
                    ],
                    "active": True
                },
                {
                    "id": "SUVINIL_001",
                    "name": "Suvinil Acrílica Fosca",
                    "brand": "Suvinil",
                    "category": "Tinta Acrílica",
                    "type": "Residencial",
                    "description": "Tinta acrílica fosca para ambientes internos",
                    "coverage": "12 m²/L",
                    "drying_time": "1 hora ao toque, 3 horas entre demãos",
                    "dilution": "Até 15% com água",
                    "application_tools": ["Rolo", "Pincel"],
                    "use_case": ["Internas", "Alvenaria", "Gesso"],
                    "features": ["Lavável", "Sem cheiro", "Boa cobertura"],
                    "colors": ["Branco", "Cores diversas"],
                    "packages": [
                        {"size": "3.6L", "price": 79.90, "stock": 30},
                        {"size": "18L", "price": 349.90, "stock": 20}
                    ],
                    "active": True
                },
                {
                    "id": "ELIT_001",
                    "name": "Elit Super Rendimento",
                    "brand": "Elit",
                    "category": "Tinta Acrílica",
                    "type": "Residencial",
                    "description": "Tinta acrílica econômica com bom rendimento",
                    "coverage": "10 m²/L",
                    "drying_time": "2 horas ao toque, 4 horas entre demãos",
                    "dilution": "Até 10% com água",
                    "application_tools": ["Rolo", "Pincel"],
                    "use_case": ["Internas", "Alvenaria"],
                    "features": ["Econômica", "Boa cobertura"],
                    "colors": ["Branco", "Cores básicas"],
                    "packages": [
                        {"size": "3.6L", "price": 59.90, "stock": 40},
                        {"size": "18L", "price": 269.90, "stock": 25}
                    ],
                    "active": True
                },
                {
                    "id": "CORAL_002",
                    "name": "Coral Esmalte Sintético",
                    "brand": "Coral",
                    "category": "Esmalte",
                    "type": "Automotiva",
                    "description": "Esmalte sintético para madeira e metal",
                    "coverage": "8 m²/L",
                    "drying_time": "4 horas ao toque, 12 horas entre demãos",
                    "dilution": "5-10% com aguarrás",
                    "application_tools": ["Pincel", "Rolo", "Pistola"],
                    "use_case": ["Madeira", "Metal", "Ferro"],
                    "features": ["Brilhante", "Durável", "Resistente"],
                    "colors": ["Branco", "Cores diversas"],
                    "packages": [
                        {"size": "900ml", "price": 45.90, "stock": 35},
                        {"size": "3.6L", "price": 159.90, "stock": 18}
                    ],
                    "active": True
                },
                {
                    "id": "PPG_001",
                    "name": "PPG Primer Universal",
                    "brand": "PPG",
                    "category": "Primer",
                    "type": "Preparação",
                    "description": "Primer universal para preparação de superfícies",
                    "coverage": "12 m²/L",
                    "drying_time": "1 hora ao toque, 2 horas entre demãos",
                    "dilution": "Até 5% com água",
                    "application_tools": ["Rolo", "Pincel", "Pistola"],
                    "use_case": ["Alvenaria", "Gesso", "Madeira", "Metal"],
                    "features": ["Aderência", "Selador", "Base água"],
                    "colors": ["Branco"],
                    "packages": [
                        {"size": "3.6L", "price": 69.90, "stock": 22},
                        {"size": "18L", "price": 299.90, "stock": 12}
                    ],
                    "active": True
                }
            ]
        }
    
    def get_all_products(self, active_only=True):
        """Retorna todos os produtos"""
        products = self.products.get('products', [])
        if active_only:
            products = [p for p in products if p.get('active', True)]
        return products
    
    def get_product_by_id(self, product_id):
        """Busca produto por ID"""
        for product in self.products.get('products', []):
            if product['id'] == product_id:
                return product
        return None
    
    def add_product(self, product_data):
        """Adiciona novo produto"""
        # Gerar ID único
        existing_ids = [p['id'] for p in self.products.get('products', [])]
        base_id = f"{product_data['brand'].upper()}_{len(existing_ids) + 1:03d}"
        
        counter = 1
        product_id = base_id
        while product_id in existing_ids:
            counter += 1
            product_id = f"{product_data['brand'].upper()}_{counter:03d}"
        
        product_data['id'] = product_id
        product_data['active'] = True
        
        self.products['products'].append(product_data)
        self.products['metadata']['last_updated'] = datetime.now().isoformat()
        self.save_products()
        
        return product_id
    
    def update_product(self, product_id, updates):
        """Atualiza produto existente"""
        for i, product in enumerate(self.products.get('products', [])):
            if product['id'] == product_id:
                self.products['products'][i].update(updates)
                self.products['metadata']['last_updated'] = datetime.now().isoformat()
                self.save_products()
                return True
        return False
    
    def delete_product(self, product_id):
        """Remove produto (marca como inativo)"""
        return self.update_product(product_id, {'active': False})
    
    def calculate_quote(self, area, product_id, coats=2, labor_included=False):
        """Calcula orçamento para um produto específico"""
        product = self.get_product_by_id(product_id)
        if not product:
            return None
        
        # Extrair rendimento
        coverage_text = product.get('coverage', '10 m²/L')
        try:
            coverage = float(coverage_text.split()[0])
        except:
            coverage = 10.0
        
        # Calcular quantidade necessária (com 10% de margem)
        liters_needed = (area / coverage / coats) * 1.1
        
        # Encontrar melhor embalagem
        packages = product.get('packages', [])
        if not packages:
            return None
        
        best_option = None
        min_waste = float('inf')
        
        for package in packages:
            size_liters = float(package['size'].replace('L', '').replace('ml', '')) 
            if 'ml' in package['size']:
                size_liters = size_liters / 1000
            
            quantity_needed = int(liters_needed / size_liters) + (1 if liters_needed % size_liters > 0 else 0)
            total_liters = quantity_needed * size_liters
            waste = total_liters - liters_needed
            total_cost = quantity_needed * package['price']
            
            if waste < min_waste or (waste == min_waste and total_cost < best_option['total_cost']):
                min_waste = waste
                best_option = {
                    'package': package,
                    'quantity': quantity_needed,
                    'total_liters': total_liters,
                    'total_cost': total_cost,
                    'waste': waste
                }
        
        # Calcular custos adicionais
        material_cost = best_option['total_cost']
        auxiliary_cost = material_cost * 0.15
        labor_cost = 0
        if labor_included:
            labor_cost = area * 8.0
        
        total_cost = material_cost + auxiliary_cost + labor_cost
        
        return {
            'product': product,
            'area': area,
            'coats': coats,
            'liters_needed': round(liters_needed, 2),
            'recommended_package': best_option,
            'costs': {
                'material': round(material_cost, 2),
                'auxiliary': round(auxiliary_cost, 2),
                'labor': round(labor_cost, 2),
                'total': round(total_cost, 2)
            },
            'quote_date': datetime.now().isoformat()
        }
    
    def export_catalog(self):
        """Exporta catálogo completo"""
        return self.products
    
    def import_catalog(self, catalog_data):
        """Importa catálogo de dados externos"""
        if isinstance(catalog_data, dict) and 'products' in catalog_data:
            self.products = catalog_data
            self.products['metadata']['last_updated'] = datetime.now().isoformat()
            self.save_products()
            return True
        return False

# Instância global do gerenciador de produtos
product_manager = ProductManager()
