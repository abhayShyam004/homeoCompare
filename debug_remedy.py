import pypdf
import re

pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"

def debug_remedy(remedy_name):
    print(f"Extraction debug for: {remedy_name}")
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        # Read last 50 pages for Zincum
        start_page = max(0, len(reader.pages) - 50)
        for i in range(start_page, len(reader.pages)):
            full_text += reader.pages[i].extract_text() + "\n"
    except Exception as e:
        print(f"Error: {e}")
        return

    # Find start
    search_term = remedy_name
    # Strict start match
    pattern = re.compile(r'(^|\n)\s*' + re.escape(search_term) + r'(?=\s*\n)', re.IGNORECASE)
    match = pattern.search(full_text)
    
    if not match:
        print(f"Could not find start of {remedy_name}")
        return
        
    start_idx = match.start()
    
    # Just Dump next 5000 chars
    chunk = full_text[start_idx:start_idx+5000]
    print("--- CHUNK START ---")
    print(chunk[:2000]) # Print first 2000
    print("--- CHUNK END ---")
    
    # Test Regex matches on this chunk
    print("\ntesting regex...")
    
    header_pattern = r"(?i)(?:Gastro[- ]?intestinal(?:[- ]?System)?|Stomach|Abdomen|Gastro[- ]?enteric|Alimentary System)"
    
    # Simple regex first
    print(f"Looking for header: {header_pattern}")
    simple_match = re.search(header_pattern, chunk)
    if simple_match:
        print(f"Found header at: {simple_match.start()} -> '{simple_match.group(0)}'")
    else:
        print("Header NOT found.")
        
    # Complex regex from v2 script
    pattern = re.compile(
        header_pattern + r"[.:\s-]+(.*?)(?=\n(?:[A-Z][a-z]+(?: [A-Z][a-z]+)*\s*\n\s*•)|(?:Modalities|Relations|Aggravation|Amelioration)|\Z)",
        re.DOTALL
    )
    
    match = pattern.search(chunk)
    if match:
        content = match.group(1).strip()
        print(f"\nCaptured Content ({len(content)} chars):\n'{content}'")
    else:
        print("\nComplex regex FAILED.")

def debug_search(term):
    print(f"Searching for term: {term}")
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for i in range(len(reader.pages)):
            full_text += reader.pages[i].extract_text() + "\n"
    except Exception as e:
        print(f"Error: {e}")
        return

    pattern = re.compile(r'\n.*' + re.escape(term) + r'.*\n', re.IGNORECASE)
    matches = list(pattern.finditer(full_text))
    print(f"Matches for '{term}':")
    for m in matches[:5]:
        print(f"  FOUND AT {m.start()}: {repr(m.group())}")
        # If it looks like a header (All Caps or Title Case), print context
        if "METALLICUM" in term.upper():
             print("--- CONTEXT ---")
             print(full_text[m.start():m.start()+4000])
             print("--- END CONTEXT ---")

if __name__ == "__main__":
    debug_search("ZINCUM METALLICUM")
