import os
import spacy
import json

nlp = spacy.load("pt_core_news_sm")

def process_text_for_knowledge(text, filename):
    doc = nlp(text)
    
    # Exemplo de extração de informações (simplificado)
    # Em um cenário real, isso seria muito mais sofisticado com regras e modelos de PLN mais avançados
    product_name = ""
    brand = ""
    features = []
    coverage = ""
    application = ""
    
    # Tentativa de extrair nome do produto e marca do nome do arquivo
    filename_lower = filename.lower()
    if "coral" in filename_lower:
        brand = "Coral"
    elif "suvinil" in filename_lower:
        brand = "Suvinil"
    elif "sherwin" in filename_lower:
        brand = "Sherwin-Williams"
    elif "elit" in filename_lower:
        brand = "Elit"
    elif "ppg" in filename_lower:
        brand = "PPG"
    elif "basf" in filename_lower:
        brand = "BASF"

    # Extração de entidades nomeadas (ex: produtos, características)
    # Isso é um exemplo básico e precisaria de refinamento para extrair informações precisas de catálogos técnicos
    for ent in doc.ents:
        if ent.label_ == "PROD" and not product_name:
            product_name = ent.text
        # Outras lógicas de extração de features, cobertura, aplicação, etc.

    # Procurar por palavras-chave para características e cobertura
    text_lower = text.lower()
    if "rendimento" in text_lower:
        # Exemplo: encontrar padrões como "rendimento de X m²/L"
        import re
        match = re.search(r"rendimento de (\d+\.?\d*)\s*m²\/l", text_lower)
        if match:
            coverage = match.group(1) + " m²/L"
    
    if "lavável" in text_lower:
        features.append("Lavável")
    if "acrílica" in text_lower:
        features.append("Acrílica")
    if "premium" in text_lower:
        features.append("Premium")
    if "automotiva" in text_lower:
        application = "Automotiva"
    elif "residencial" in text_lower or "parede" in text_lower:
        application = "Residencial"

    # Se o nome do produto não foi encontrado por NER, tentar do nome do arquivo
    if not product_name:
        product_name = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
        # Limpar o nome do produto
        if brand and product_name.lower().startswith(brand.lower()):
            product_name = product_name[len(brand):].strip()
        product_name = product_name.title()

    return {
        "filename": filename,
        "brand": brand,
        "product_name": product_name,
        "type": application, # Usando application como tipo inicial
        "coverage": coverage,
        "features": list(set(features)) # Remover duplicatas
    }

if __name__ == "__main__":
    extracted_texts_dir = "/home/ubuntu/extracted_texts"
    structured_knowledge = []

    for filename in os.listdir(extracted_texts_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(extracted_texts_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            knowledge_entry = process_text_for_knowledge(text, filename)
            structured_knowledge.append(knowledge_entry)

    # Salvar a base de conhecimento estruturada em um arquivo JSON
    output_json_path = "/home/ubuntu/structured_knowledge.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_knowledge, f, ensure_ascii=False, indent=4)

    print(f"Base de conhecimento estruturada salva em {output_json_path}")

    # Exemplo de como a base de conhecimento poderia ser usada (para demonstração)
    # print("\n--- Exemplo de entradas da Base de Conhecimento ---")
    # for entry in structured_knowledge[:5]: # Mostrar as primeiras 5 entradas
    #     print(json.dumps(entry, ensure_ascii=False, indent=2))
