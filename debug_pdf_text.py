import pypdf
import sys
import re

pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"

def debug_extraction():
    try:
        reader = pypdf.PdfReader(pdf_path)
        print(f"Opening PDF: {pdf_path}")
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return

    # We will look at the first few pages or search for a specific remedy to see the layout
    # Aconite is usually early.
    
    full_text = ""
    # Extract first 50 pages to be safe and cover Aconite
    for i in range(min(50, len(reader.pages))):
        full_text += reader.pages[i].extract_text() + "\n"
        
    print("--- RAW TEXT SAMPLE (ACONITUM) ---")
    
    # Find ACONITUM NAPELLUS
    match = re.search(r"ACONITUM NAPELLUS", full_text)
    if match:
        start = match.start()
        # Print next 2000 characters
        snippet = full_text[start:start+3000]
        print(snippet)
        print("-" * 40)
        
        # Test the regex on this snippet
        print("Testing Regex on snippet:")
        gi_match = re.search(r"(?i)(Gastro[- ]?intestinal|Gastro[- ]?enteric)[.\s:-]+(.*?)(?=\n[A-Z][a-z]+[.:]|\n[A-Z]{3,}|\Z)", snippet, re.DOTALL)
        if gi_match:
            print(f"MATCH FOUND: '{gi_match.group(2)}'")
        else:
            print("NO MATCH FOUND")
            
    else:
        print("ACONITUM NAPELLUS not found in first 50 pages.")

if __name__ == "__main__":
    debug_extraction()
