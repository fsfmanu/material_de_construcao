import PyPDF2
import os

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Erro ao extrair texto de {pdf_path}: {e}")
    return text

if __name__ == "__main__":
    catalogs_dir = "/home/ubuntu/catalogs"
    output_dir = "/home/ubuntu/extracted_texts"
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(catalogs_dir):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(catalogs_dir, filename)
            extracted_text = extract_text_from_pdf(pdf_path)
            
            output_filename = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as outfile:
                outfile.write(extracted_text)
            print(f"Texto extraído de {filename} e salvo em {output_path}")
