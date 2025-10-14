import os
import spacy
import json
import re

nlp = spacy.load("pt_core_news_sm")

def extract_product_info(text, filename):
    doc = nlp(text)
    info = {
        "filename": filename,
        "brand": "",
        "product_name": "",
        "type": "",
        "coverage": "",
        "drying_time": "",
        "dilution": "",
        "application_tools": [],
        "use_case": [],
        "features": [],
        "description": ""
    }

    # Tentar extrair marca do nome do arquivo ou do texto
    filename_lower = filename.lower()
    if "coral" in filename_lower or "coral" in text.lower():
        info["brand"] = "Coral"
    elif "suvinil" in filename_lower or "suvinil" in text.lower():
        info["brand"] = "Suvinil"
    elif "sherwin" in filename_lower or "sherwin" in text.lower():
        info["brand"] = "Sherwin-Williams"
    elif "elit" in filename_lower or "elit" in text.lower():
        info["brand"] = "Elit"
    elif "ppg" in filename_lower or "ppg" in text.lower():
        info["brand"] = "PPG"
    elif "basf" in filename_lower or "basf" in text.lower():
        info["brand"] = "BASF"

    # Extração de nome do produto (mais robusta)
    # Tentar encontrar padrões como 'Produto X' ou 'Linha Y'
    product_name_matches = re.findall(r'(?:tinta|esmalte|verniz|selador|massa|primer)\s+([\w\s-]+?)(?:\s+(?:acrílica|látex|epóxi|sintético|premium|econômica|automotiva|residencial|base)|\s*\(|\s*\d|\s*\b)', text, re.IGNORECASE)
    if product_name_matches:
        info["product_name"] = max(product_name_matches, key=len).strip()
    elif info["brand"] and len(text.split('\n')[0]) < 100: # Se a primeira linha for curta, pode ser o nome
        info["product_name"] = text.split('\n')[0].strip()
    else:
        info["product_name"] = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ").title()
        if info["brand"] and info["product_name"].lower().startswith(info["brand"].lower()):
            info["product_name"] = info["product_name"][len(info["brand"]):].strip()

    # Extração de tipo (residencial/automotiva)
    if re.search(r'automotiva|repintura automotiva|veículos', text, re.IGNORECASE):
        info["type"] = "Automotiva"
    elif re.search(r'residencial|paredes|tetos|pisos|imóveis|construção civil', text, re.IGNORECASE):
        info["type"] = "Residencial"

    # Extração de rendimento (coverage)
    coverage_matches = re.findall(r'rendimento(?:\s+de)?\s*(\d+[.,]?\d*\s*m²(?:/l| por litro)?)', text, re.IGNORECASE)
    if coverage_matches:
        info["coverage"] = "; ".join(list(set(c.replace(',', '.') for c in coverage_matches)))
    else:
        coverage_matches = re.findall(r'(\d+[.,]?\d*\s*m²(?:/l| por litro)?)', text, re.IGNORECASE)
        if coverage_matches:
            info["coverage"] = "; ".join(list(set(c.replace(',', '.') for c in coverage_matches)))

    # Extração de tempo de secagem (drying_time)
    drying_time_matches = re.findall(r'secagem:\s*(.*?)(?:\.|\n|\r)', text, re.IGNORECASE)
    if drying_time_matches:
        info["drying_time"] = "; ".join(list(set(d.strip() for d in drying_time_matches)))
    else:
        drying_time_matches = re.findall(r'(?:ao toque|entre demãos|final):\s*(\d+\s*(?:min|horas|dias))', text, re.IGNORECASE)
        if drying_time_matches:
            info["drying_time"] = "; ".join(list(set(d.strip() for d in drying_time_matches)))

    # Extração de diluição (dilution)
    dilution_matches = re.findall(r'diluição:\s*(.*?)(?:\.|\n|\r)', text, re.IGNORECASE)
    if dilution_matches:
        info["dilution"] = "; ".join(list(set(d.strip() for d in dilution_matches)))
    else:
        dilution_matches = re.findall(r'(\d+-\d+%\s+com\s+\w+)', text, re.IGNORECASE)
        if dilution_matches:
            info["dilution"] = "; ".join(list(set(d.strip() for d in dilution_matches)))

    # Extração de ferramentas de aplicação (application_tools)
    tools_keywords = ["rolo", "pincel", "trincha", "pistola", "desempenadeira", "espátula"]
    for keyword in tools_keywords:
        if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE) and keyword not in info["application_tools"]:
            info["application_tools"].append(keyword.capitalize())

    # Extração de uso (use_case)
    use_case_keywords = ["internas", "externas", "madeira", "metal", "alvenaria", "gesso", "drywall", "concreto", "fibrocimento", "azulejo", "telhado", "piso"]
    for keyword in use_case_keywords:
        if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE) and keyword not in info["use_case"]:
            info["use_case"].append(keyword.capitalize())

    # Extração de características (features)
    feature_keywords = ["lavável", "acrílica", "epóxi", "sintética", "fosca", "semibrilho", "brilhante", "acetinada", "premium", "econômica", "antimofo", "antibactéria", "resistente", "durável", "secagem rápida", "sem cheiro", "base água", "base solvente"]
    for keyword in feature_keywords:
        if re.search(r'\b' + keyword + r'\b', text, re.IGNORECASE) and keyword not in info["features"]:
            info["features"].append(keyword.capitalize())

    # Extração de uma breve descrição (primeiras frases ou parágrafos)
    sentences = [s.text for s in doc.sents if len(s.text.strip()) > 10]
    if sentences:
        info["description"] = " ".join(sentences[:2]) # Pegar as duas primeiras frases como descrição

    return info

if __name__ == "__main__":
    extracted_texts_dir = "/home/ubuntu/extracted_texts"
    structured_knowledge = []

    for filename in os.listdir(extracted_texts_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(extracted_texts_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            knowledge_entry = extract_product_info(text, filename)
            structured_knowledge.append(knowledge_entry)

    output_json_path = "/home/ubuntu/structured_knowledge_advanced.json"
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_knowledge, f, ensure_ascii=False, indent=4)

    print(f"Base de conhecimento estruturada (avançada) salva em {output_json_path}")

    # Exemplo de como a base de conhecimento poderia ser usada (para demonstração)
    print("\n--- Exemplo de entradas da Base de Conhecimento Avançada ---")
    for entry in structured_knowledge[:3]: # Mostrar as primeiras 3 entradas
        print(json.dumps(entry, ensure_ascii=False, indent=2))
