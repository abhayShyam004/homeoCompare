import json
import os
import re
import shutil
import sys

def fill_missing_data(json_path, pdf_path):
    print(f"Loading JSON from {json_path}...")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    print(f"Loading PDF from {pdf_path}...")
    full_text = ""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        print(f"PDF has {len(reader.pages)} pages. Extracting text...")
        for i, page in enumerate(reader.pages):
            full_text += page.extract_text() + "\n"
            if i % 50 == 0:
                print(f"Processed {i} pages...", end='\r')
        print("Text extraction complete.")
    except ImportError:
        print("Error: pypdf not installed. Run 'pip install pypdf'")
        return
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    # Normalize text vaguely (replace multiple newlines with single, etc if needed, 
    # but keep structure for header detection)
    
    updates_made = 0
    
    # Regex for finding remedy blocks is hard because they aren't strictly marked.
    # But usually CAPITALIZED NAME like "ABROTANUM" starts a block.
    # We will search for the specific remedy name to find its approximate location.
    
    print("Scanning for missing data...")
    
    keys = list(data.keys())
    
    for i, key in enumerate(keys):
        entry = data[key]
        
        # Check if we need to fill anything
        need_gastro = not entry.get("gastro intestinal system")
        need_cardio = not entry.get("cardio vascular system")
        
        if not need_gastro and not need_cardio:
            continue
            
        print(f"Processing {key}...")
        
        # Find Remedy in Text
        # Look for the Key (Remedy Name) in ALL CAPS, likely on its own line or at start of line
        # We'll search case-insensitive but prefer exact match
        
        # Simple heuristic: split text by the Remedy Name
        # This is risky if name appears multiple times. 
        # Usually checking for "\nNAME" works best.
        
        search_pattern = re.escape(key)
        # Find all occurrences
        matches = list(re.finditer(search_pattern, full_text, re.IGNORECASE))
        
        if not matches:
            print(f"  Warning: Could not find remedy '{key}' in PDF text.")
            continue
            
        # Assume the main entry is the one with the most text following it that looks like symptoms?
        # Or just take the first "heading" style match. 
        # Often headings are ALL CAPS.
        
        best_match = None
        for m in matches:
            # Check if it looks like a header (surrounded by newlines, or at start)
            # This is heuristic.
            best_match = m
            break # Try first one for now
            
        if not best_match:
            continue
            
        start_idx = best_match.end()
        
        # Find the START of the NEXT remedy to bound our search
        # We can look for the next key in the list?
        # Not reliable if keys aren't in order.
        # Instead, just search forward for a bit or until next known header?
        # Let's search for next known remedy name from our list? 
        # That's O(N^2).
        # Better: just look for the next "ALL CAPS LINE" that matches a known remedy?
        
        # We'll take a chunk of text, say 5000 chars, to search in.
        search_chunk = full_text[start_idx : start_idx + 10000] 
        
        # Define regex for relevant sections
        # Patterns seen in Allen's: "Gastro-intestinal.--" "Heart.--" "Commotion.--" etc.
        # Sometimes "GI System" etc.
        
        if need_gastro:
            # Look for Gastro-Intestinal
            # Pattern: (Gastro-intestinal|Stomach|Abdomen|Gastro-enteric).*?(?=\n[A-Z][a-z]+|\n[A-Z]+)
            # We want to catch "Gastro-intestinal.-- content content"
            
            gi_match = re.search(r"(?i)(Gastro[- ]?intestinal|Gastro[- ]?enteric)[.\s:-]+(.*?)(?=\n[A-Z][a-z]+[.:]|\n[A-Z]{3,}|\Z)", search_chunk, re.DOTALL)
            if gi_match:
                extracted = gi_match.group(2).strip()
                extracted = extracted.replace("\n", " ").replace("  ", " ")
                # Check if it's too short or garbage
                if len(extracted) > 5:
                    entry["gastro intestinal system"] = extracted
                    print(f"  [+] Found Gastro: {extracted[:30]}...")
                    updates_made += 1
            else:
                 print("  [-] Gastro section not found.")

        if need_cardio:
            # Look for Cardio-Vascular / Heart
            # Pattern: (Cardio-vascular|Heart|Circulation).*?
            cv_match = re.search(r"(?i)(Cardio[- ]?vascular|Heart|Circulation)[.\s:-]+(.*?)(?=\n[A-Z][a-z]+[.:]|\n[A-Z]{3,}|\Z)", search_chunk, re.DOTALL)
            if cv_match:
                extracted = cv_match.group(2).strip()
                extracted = extracted.replace("\n", " ").replace("  ", " ")
                if len(extracted) > 5:
                    entry["cardio vascular system"] = extracted
                    print(f"  [+] Found Cardio: {extracted[:30]}...")
                    updates_made += 1
            else:
                print("  [-] Cardio section not found.")

    if updates_made > 0:
        print(f"\nTotal updates made: {updates_made}")
        backup_path = json_path + ".bak"
        shutil.copy(json_path, backup_path)
        print(f"Backup saved to {backup_path}")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully updated {json_path}")
    else:
        print("\nNo updates were found or made.")

if __name__ == "__main__":
    json_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\app\allens_keynotes.json"
    pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"
    
    fill_missing_data(json_path, pdf_path)
