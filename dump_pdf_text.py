from pypdf import PdfReader
import json

def extract_text_to_file(pdf_path, output_txt):
    try:
        reader = PdfReader(pdf_path)
        with open(output_txt, 'w', encoding='utf-8') as f:
            for page in reader.pages:
                text = page.extract_text()
                f.write(text)
                f.write("\n---PAGE BREAK---\n")
        print(f"Text extracted to {output_txt}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_text_to_file("relationship-of-remedies-dr-rgibson-miller.pdf", "pdf_content_dump.txt")
