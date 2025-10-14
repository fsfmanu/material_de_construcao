import os
import spacy
import json
import re

nlp = spacy.load("pt_core_news_sm")

def extract_pisos_info(text, filename):
    doc = nlp(text)
    product_info = {
        "filename": filename,
        "brand": "",
        "product_name": "",
        "type": "",
        "category": "",
        "size": "",
        "pei_class": "",
        "slip_resistance": "",
        "water_absorption": "",
        "features": [],
        "use_case": [],
        "price_range": "",
        "installation": "",
        "maintenance": "",
        "description": ""
    }

    # 1. Extrair Marca (do nome do arquivo ou do texto)
    filename_lower = filename.lower()
    if "eliane" in filename_lower or "eliane" in text.lower():
        product_info["brand"] = "Eliane"
    elif "portinari" in filename_lower or "portinari" in text.lower():
        product_info["brand"] = "Portinari"
    elif "biancogres" in filename_lower or "biancogres" in text.lower():
        product_info["brand"] = "Biancogres"
    elif "durafloor" in filename_lower or "durafloor" in text.lower():
        product_info["brand"] = "Durafloor"
    elif "tarkett" in filename_lower or "tarkett" in text.lower():
        product_info["brand"] = "Tarkett"
    elif "indusparquet" in filename_lower or "indusparquet" in text.lower():
        product_info["brand"] = "Indusparquet"

    # 2. Extrair Nome do Produto
    product_name_patterns = [
        r'(piso\s+\w+\s+\w+)', r'(porcelanato\s+\w+\s+\w+)', r'(revestimento\s+\w+\s+\w+)',
        r'(laminado\s+\w+)', r'(vinílico\s+\w+)', r'(madeira\s+\w+)', r'(mármore\s+\w+)'
    ]
    for pattern in product_name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            product_info["product_name"] = match.group(0).title()
            break
    
    if not product_info["product_name"]:
        product_info["product_name"] = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
        if product_info["brand"] and product_info["product_name"].lower().startswith(product_info["brand"].lower()):
            product_info["product_name"] = product_info["product_name"][len(product_info["brand"]):].strip()

    # 3. Extrair Tipo (Cerâmico, Porcelanato, Laminado, Vinílico, Madeira, Pedra Natural, Cimento)
    types = ["cerâmico", "porcelanato", "laminado", "vinílico", "madeira", "pedra natural", "cimento"]
    for t in types:
        if t in text.lower():
            product_info["type"] = t.title()
            break

    # 4. Extrair Categoria (Piso, Revestimento)
    if "piso" in text.lower():
        product_info["category"] = "Piso"
    elif "revestimento" in text.lower():
        product_info["category"] = "Revestimento"

    # 5. Extrair Tamanho
    size_match = re.search(r'(\d+x\d+cm|\d+\s*x\s*\d+\s*cm)', text, re.IGNORECASE)
    if size_match:
        product_info["size"] = size_match.group(0).replace(" ", "")

    # 6. Extrair Classe PEI
    pei_match = re.search(r'pei\s*(\d)', text, re.IGNORECASE)
    if pei_match:
        product_info["pei_class"] = pei_match.group(1)

    # 7. Extrair Resistência ao Escorregamento (Slip Resistance)
    slip_match = re.search(r'(r\d{1,2})', text, re.IGNORECASE)
    if slip_match:
        product_info["slip_resistance"] = slip_match.group(1).upper()

    # 8. Extrair Absorção de Água
    water_abs_match = re.search(r'absorção de água:\s*(<|>)?\s*(\d+[.,]?\d*%)', text, re.IGNORECASE)
    if water_abs_match:
        product_info["water_absorption"] = water_abs_match.group(0)

    # 9. Extrair Características (polido, acetinado, esmaltado, antiderrapante, impermeável, durável)
    feature_keywords = ["polido", "acetinado", "esmaltado", "antiderrapante", "impermeável", "durável", "fácil limpeza", "baixa absorção", "efeito madeira", "sistema click", "confortável", "isolamento acústico", "natural", "elegante", "moderno", "industrial"]
    for fk in feature_keywords:
        if fk in text.lower() and fk.title() not in product_info["features"]:
            product_info["features"].append(fk.title())
            
    # 10. Extrair Casos de Uso (sala, quarto, cozinha, banheiro, área de serviço, varanda, hall, escritório)
    use_case_keywords = ["sala", "quarto", "cozinha", "banheiro", "área de serviço", "varanda", "hall", "escritório", "comercial", "residencial", "externo", "interno"]
    for uc in use_case_keywords:
        if uc in text.lower() and uc.title() not in product_info["use_case"]:
            product_info["use_case"].append(uc.title())

    # 11. Extrair Instalação
    installation_match = re.search(r'instalação:\s*(.*?)(?:\.|\n|\r)', text, re.IGNORECASE)
    if installation_match:
        product_info["installation"] = installation_match.group(1).strip()

    # 12. Extrair Manutenção
    maintenance_match = re.search(r'manutenção:\s*(.*?)(?:\.|\n|\r)', text, re.IGNORECASE)
    if maintenance_match:
        product_info["maintenance"] = maintenance_match.group(1).strip()

    # 13. Extrair uma breve descrição (primeiras frases ou parágrafos)
    sentences = [s.text for s in doc.sents if len(s.text.strip()) > 10]
    if sentences:
        product_info["description"] = " ".join(sentences[:2])

    # Limpar e garantir unicidade nas listas
    product_info["features"] = list(set(product_info["features"]))
    product_info["use_case"] = list(set(product_info["use_case"]))

    return product_info

if __name__ == "__main__":
    extracted_texts_dir = "/home/ubuntu/extracted_texts_pisos"
    structured_knowledge = []

    # Criar um diretório de exemplo para pisos se não existir
    if not os.path.exists(extracted_texts_dir):
        os.makedirs(extracted_texts_dir)
        # Criar alguns arquivos de texto de exemplo para pisos
        with open(os.path.join(extracted_texts_dir, "pisos_ceramico_eliane.txt"), "w", encoding="utf-8") as f:
            f.write("Piso Cerâmico Eliane - Coleção Mediterrâneo. Tipo: Cerâmico. Categoria: Revestimento. Tamanho: 60x60cm. PEI: 4. Resistência ao escorregamento: R10. Absorção de água: 6-10%. Características: Esmaltado, fácil limpeza, durável. Uso: Interno, externo, áreas de alto tráfego. Instalação: Argamassa ACII. Manutenção: Limpeza diária com água e sabão neutro.")
        with open(os.path.join(extracted_texts_dir, "porcelanato_portinari_madeira.txt"), "w", encoding="utf-8") as f:
            f.write("Porcelanato Portinari - Linha Amadeirados. Tipo: Porcelanato. Categoria: Piso. Tamanho: 20x120cm. PEI: 5. Resistência ao escorregamento: R9. Absorção de água: <0.5%. Características: Acetinado, efeito madeira, retificado, resistente à água. Uso: Sala, quarto, cozinha, banheiro. Instalação: Argamassa ACIII. Manutenção: Pano úmido.")
        with open(os.path.join(extracted_texts_dir, "laminado_durafloor_carvalho.txt"), "w", encoding="utf-8") as f:
            f.write("Piso Laminado Durafloor - Essencial Carvalho. Tipo: Laminado. Categoria: Piso. Tamanho: 19x134cm. PEI: 3. Características: Sistema click, fácil instalação, confortável, hipoalergênico. Uso: Quartos, salas. Instalação: Flutuante com manta. Manutenção: Aspirador de pó, pano levemente úmido.")
        print(f"Diretório {extracted_texts_dir} criado com arquivos de exemplo.")

    if not os.path.exists(extracted_texts_dir):
        print(f"Diretório {extracted_texts_dir} não encontrado. Certifique-se de que os textos foram extraídos.")
    else:
        for filename in os.listdir(extracted_texts_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(extracted_texts_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                
                knowledge_entry = extract_pisos_info(text, filename)
                structured_knowledge.append(knowledge_entry)

        output_json_path = "/home/ubuntu/structured_pisos_knowledge_advanced.json"
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(structured_knowledge, f, ensure_ascii=False, indent=4)

        print(f"Base de conhecimento estruturada (avançada) para pisos salva em {output_json_path}")

        print("\n--- Exemplo de entradas da Base de Conhecimento Avançada para Pisos ---")
        for entry in structured_knowledge[:3]: # Mostrar as primeiras 3 entradas
            print(json.dumps(entry, ensure_ascii=False, indent=2))

