import json
import os
import sys

# Force unbuffered output
sys.stdout.reconfigure(encoding='utf-8')

def check_json_consistency(json_path):
    print(f"Checking {json_path}...", flush=True)
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return None

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

    issues = []
    print(f"Total entries: {len(data)}", flush=True)

    for key, entry in data.items():
        if entry.get("name") != key:
            issues.append(f"[{key}] Name mismatch: '{entry.get('name')}' vs key '{key}'")
        
        if not entry.get("description"):
            # Some might legitimately not have it, but flagging it.
            # issues.append(f"[{key}] Missing description") 
            pass 

    if issues:
        print("\n=== Internal Consistency Issues ===")
        for i in issues[:20]:
            print(i)
        if len(issues) > 20:
            print(f"... and {len(issues) - 20} more.")
    else:
        print("\nNo internal consistency issues found.")

    return data

def check_pdf_match(data, pdf_path):
    print(f"\nChecking against PDF: {pdf_path}", flush=True)
    if not os.path.exists(pdf_path):
        print("PDF file not found.")
        return

    text = ""
    try:
        import pypdf
        print("Using pypdf...", flush=True)
        reader = pypdf.PdfReader(pdf_path)
        # Only read first 10 pages for a quick test if it's huge? No, user wants all issues.
        # But reading a huge PDF might take time.
        # Let's read all but print progress.
        num_pages = len(reader.pages)
        print(f"PDF has {num_pages} pages.", flush=True)
        
        for i, page in enumerate(reader.pages):
            text += page.extract_text() + "\n"
            if i % 10 == 0:
                print(f"Processed {i}/{num_pages} pages...", end='\r', flush=True)
                
    except ImportError:
        print("pypdf not installed. Please ask user to install it or use another method.")
        return
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    print(f"\nExtracted {len(text)} characters from PDF.", flush=True)
    
    text_upper = text.upper()
    missing_in_pdf = []
    
    # Check a sample first
    print("Verifying 5 sample keys...", flush=True)
    sample_keys = list(data.keys())[:5]
    for k in sample_keys:
        found = k in text_upper
        print(f"  {k}: {'Found' if found else 'NOT FOUND'}")

    # Full check
    print("Running full check...", flush=True)
    for key in data.keys():
        if key not in text_upper:
            missing_in_pdf.append(key)

    if missing_in_pdf:
        print("\n=== Remedies NOT found in PDF text ===")
        for m in missing_in_pdf:
            print(m)
    else:
        print("\nAll remedy names found in PDF.")

if __name__ == "__main__":
    json_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\app\medicines\allens_keynotes.json"
    pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"
    
    data = check_json_consistency(json_path)
    if data:
        check_pdf_match(data, pdf_path)
