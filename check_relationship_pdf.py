from pypdf import PdfReader

def extract_pdf_sample(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        print(f"Total Pages: {len(reader.pages)}")
        
        # Extract text from first few pages to see structure
        for i in range(min(5, len(reader.pages))):
            print(f"\n--- Page {i+1} ---")
            text = reader.pages[i].extract_text()
            print(text[:1000]) # First 1000 chars per page
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_pdf_sample("relationship-of-remedies-dr-rgibson-miller.pdf")
