import json
import os
import re
import shutil
import pypdf

def normalize_name(name):
    """Normalize remedy name for fuzzy matching."""
    # Replace double dashes with single or space
    name = name.replace("--", "-")
    return name

def get_remedy_boundaries(full_text, remedy_keys):
    """
    Finds the start index of each remedy in the PDF text.
    Returns a list of (remedy_key, start_index) sorted by index.
    """
    print("Mapping remedy locations in PDF...")
    boundaries = []
    
    # We look for the remedy name in ALL CAPS, appearing on a line
    # (possibly surrounded by whitespace).
    # Some names in PDF might be slightly different, so we try a few variations.
    
    for key in remedy_keys:
        search_terms = [
            key, 
            key.replace("--", "-"),
            key.replace("--", " "),
            key.split(" ")[0] # Fallback: search just the first word? No, too dangerous.
        ]
        if "ACIDUM" in key:
             # Try "ACIDUM X" vs "X ACIDUM"? Allen's usually uses "ACIDUM X" or "X ACID"
             # Actually JSON has "PHOSPHORICUM ACIDUM". PDF might have "PHOSPHORIC ACID".
             pass
        
        found = False
        for term in search_terms:
            # Regex: Newline, optional whitespace, Term, optional whitespace, Newline
            # Or Term at start of text.
            pattern = re.compile(r'(^|\n)\s*' + re.escape(term) + r'(?=\s*\n)', re.IGNORECASE)
            match = pattern.search(full_text)
            if match:
                # We want the start of the NAME.
                # match.start() counts from the newline prefix.
                # adjust index to point to the name.
                idx = match.start()
                if full_text[idx] == '\n': 
                    idx += 1
                boundaries.append((key, idx))
                found = True
                break
        
        if not found:
            # Try looser match: Just the name in all caps?
            # Be careful not to match references in text.
            # Usually remedy headers are Uppercase.
            pattern = re.compile(r'\n' + re.escape(search_terms[1]).upper() + r'(?=\s*\n)')
            match = pattern.search(full_text)
            if match:
                 boundaries.append((key, match.start() + 1))
                 found = True

        if not found:
             print(f"  [!] Could not locate start of '{key}'")
    
    # Sort by index
    boundaries.sort(key=lambda x: x[1])
    
    # Add an end sentinel
    boundaries.append(("END", len(full_text)))
    
    print(f"Mapped {len(boundaries)-1} remedies.")
    return boundaries

def extract_section(text, section_type):
    """
    Extracts content for a specific section type (Gastro or Cardio).
    """
    if section_type == "Gastro":
        # pattern matches: Gastro-Intestinal, Stomach, Abdomen, GI System
        # We handle "Gastro-intestinal System" by allowing optional "System"
        # We capture content until we hit a clear new Header (Title Case followed by bullet)
        # or a large gap.
        
        # Regex explanation:
        # (?i) : ignore case
        # (?: ... ) : non-capturing group for alternatives
        # Gastro[- ]?intestinal(?:[- ]?System)? : Matches "Gastro-intestinal" or "Gastro-intestinal System"
        # Stomach|Abdomen|Alimentary System : alternatives
        # [.:\s-]+ : separator (newlines, dashes, etc)
        # (.*?) : Content (group 1)
        # (?= ... ) : Lookahead for stop condition
        # Stop condition: 
        #   \n[A-Z][A-Za-z ]+\n•  -> Next Header (Title Case) followed by bullet
        #   \n[A-Z]{3,}\n        -> Next Remedy (ALL CAPS) - though our chunk should limit this.
        #   \Z                   -> End of text
        
        header_pattern = r"(?i)(?:Gastro[- ]?intestinal(?:[- ]?System)?|Stomach|Abdomen|Gastro[- ]?enteric|Alimentary System)"
    elif section_type == "Cardio":
        header_pattern = r"(?i)(?:Cardio[- ]?vascular(?:[- ]?System)?|Heart|Circulation|Pulse)"
    else:
        return None

    # We iterate to find the header, then capture text.
    # We want to be careful about "System" being split.
    
    pattern = re.compile(
        header_pattern + r"[.:\s-]+(.*?)(?=\n(?:[A-Z][a-z]+(?: [A-Z][a-z]+)*\s*\n\s*•)|(?:Modalities|Relations|Aggravation|Amelioration)|\Z)",
        re.DOTALL
    )
    
    match = pattern.search(text)
    if match:
        content = match.group(1).strip()
        
        # Cleanup:
        # Remove "System •" if it was captured at the start (residue)
        if content.lower().startswith("system"):
            content = re.sub(r"^system\s*[•\-]?\s*", "", content, flags=re.IGNORECASE)
        
        # Remove leading bullets
        content = re.sub(r"^[•\-]\s*", "", content)
        
        # Normalize newlines to spaces
        content = content.replace("\n", " ").strip()
        
        # Check if content is valid (longer than 5 chars, not just a label)
        if len(content) > 5:
            return content
            
    return None

def fill_missing_data(json_path, pdf_path):
    print(f"Loading JSON from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loading PDF from {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    # 1. Map Remedies
    keys = list(data.keys())
    boundaries = get_remedy_boundaries(full_text, keys)
    
    # create a lookup for boundaries {key: (start, end)}
    remedy_ranges = {}
    for i in range(len(boundaries) - 1):
        rem_key, start = boundaries[i]
        next_key, end = boundaries[i+1]
        remedy_ranges[rem_key] = (start, end)

    updates_made = 0
    
    print("Processing remedies...")
    for key, entry in data.items():
        need_gastro = not entry.get("gastro intestinal system") or entry.get("gastro intestinal system") == "System •"
        need_cardio = not entry.get("cardio vascular system") or entry.get("cardio vascular system") == "System •"
        
        if not (need_gastro or need_cardio):
            continue

        if key not in remedy_ranges:
            continue
            
        start, end = remedy_ranges[key]
        # Extract chunk
        chunk = full_text[start:end]
        
        # print(f"DEBUG: Analyzing {key} (Size: {len(chunk)})")
        
        if need_gastro:
            content = extract_section(chunk, "Gastro")
            if content:
                entry["gastro intestinal system"] = content
                print(f"  [+] {key}: Filled Gastro ({len(content)} chars)")
                updates_made += 1
        
        if need_cardio:
            content = extract_section(chunk, "Cardio")
            if content:
                entry["cardio vascular system"] = content
                print(f"  [+] {key}: Filled Cardio ({len(content)} chars)")
                updates_made += 1

    if updates_made > 0:
        print(f"\nTotal updates made: {updates_made}")
        backup_path = json_path + ".bak_v2"
        shutil.copy(json_path, backup_path)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("JSON updated successfully.")
    else:
        print("No updates found.")

if __name__ == "__main__":
    json_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\app\allens_keynotes.json"
    pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"
    fill_missing_data(json_path, pdf_path)
