import json
import os
import re
import shutil
import pypdf

def get_remedy_boundaries(full_text, remedy_keys_set):
    """
    Finds the TRUE start index of each remedy in the PDF text, avoiding TOC.
    Returns a sorted list of (remedy_key, start_index).
    """
    print("Mapping remedy locations in PDF (ignoring TOC)...")
    boundaries = []
    
    # Common words that appear *after* a real remedy header
    # Based on Allen's Keynotes structure
    validating_keywords = [
        "Constitution", "Mental", "Physical", "Mind", "Head", "Eyes", "Ears", 
        "Nose", "Face", "Mouth", "Throat", "Stomach", "Abdomen", "Rectum", 
        "Urinary", "Sexual", "Female", "Male", "Respiratory", "Chest", "Heart"
    ]
    
    # We'll normalize keys for comparison
    keys_normalized = {k.replace("--", " ").upper(): k for k in remedy_keys_set}
    keys_search = list(keys_normalized.keys())
    
    # We scan the text for lines that are exactly a remedy name (CASE INSENSITIVE or UPPER)
    # Then verify it's not a TOC entry.
    
    # Regex to find potential headers:
    # Standalone line with some chars
    # We optimize by NOT using regex for every single key over the whole text.
    # Instead, we find "All Caps Lines" that match our keys.
    
    # Pattern: Newline, Title/Caps text, Newline.
    # Note: Text extraction usually puts headers on their own line.
    
    lines = full_text.split('\n')
    current_pos = 0
    
    for i, line in enumerate(lines):
        line_clean = line.strip().replace("--", " ").upper()
        # Calculate start position of this line in full_text
        # (Approximate if split consumed newlines, but we can search or track)
        # Better to just use regex on full text to find indices? 
        # No, line iteration is good for logic, but hard for indices.
        pass

    # Let's revert to regex on full text for indices, but use logic to filter.
    
    for key in remedy_keys_set:
        # Search variations
        variations = [key, key.replace("--", " ")]
        
        found_indices = []
        for term in variations:
            # Look for TERM on its own line
            pattern = re.compile(r'\n\s*' + re.escape(term) + r'\s*\n', re.IGNORECASE)
            for match in pattern.finditer(full_text):
                found_indices.append(match.start())
        
        if not found_indices:
             # Try split keys? "Amylenum Nitrosum"
             # sometimes names are split?
             continue
             
        best_idx = -1
        
        # Heuristic to pick the "Real" one
        for idx in found_indices:
            # Check context following the match (first 500 chars)
            context = full_text[idx:idx+800]
            
            # Check 1: Does it look like TOC?
            # TOC entry is usually followed immediately by another remedy name or page number.
            # Real entry is followed by "Common Name", "Family", or sections "Mind", "Head" etc.
            
            score = 0
            for kw in validating_keywords:
                if kw in context:
                    score += 1
            
            # Check for bullet points (common in text)
            if "•" in context:
                score += 2
                
            # If we see multiple other remedy names in the context, it's likely TOC of Index
            # (We won't implement this negative check for now, positive score is safer)
            
            if score >= 1: # Found at least one keyword or bullet
                best_idx = idx
                # If we find a good one, we prefer the "Main" one which usually has more keywords.
                # But typically the first "good" one after the TOC is the one.
                # Actually, Index is at the end. TOC is at start.
                # So we want the first match that looks "Real".
                break
        
        if best_idx != -1:
            # Adjust index to skip the newline
            boundaries.append((key, best_idx + 1))
        # else:
            # print(f"  [!] Could not locate body for '{key}'")

    # Sort
    boundaries.sort(key=lambda x: x[1])
    
    # Filter duplicates (if multiple variations matched same spot)
    unique_boundaries = []
    seen_indices = set()
    for k, idx in boundaries:
        if idx not in seen_indices:
            unique_boundaries.append((k, idx))
            seen_indices.add(idx)
            
    # Add end sentinel
    unique_boundaries.append(("END", len(full_text)))

    print(f"Mapped {len(unique_boundaries)-1} remedies with content validation.")
    return unique_boundaries

def extract_section_content(text, section_type):
    # Regex designed for the "Header ... Content" flow
    # Content usually starts with a bullet • or just text
    
    patterns = []
    
    if section_type == "Gastro":
        # Variations found in Allen's
        headers = [
            r"Gastro[- ]?intestinal System",
            r"Gastro[- ]?intestinal",
            r"Stomach",
            r"Abdomen",
            r"Alimentary System",
            r"Gastro[- ]?enteric"
        ]
    elif section_type == "Cardio":
        headers = [
            r"Cardio[- ]?vascular System",
            r"Cardio[- ]?vascular",
            r"Heart",
            r"Circulation",
            r"Pulse"
        ]
    else:
        return None

    # We want to match:
    # \n HEADER \n (optional junk) • (CONTENT) next_section_header
    
    # Construct a big regex for headers
    header_group = "(?:" + "|".join(headers) + ")"
    
    # 1. Header followed by content until next Main Section (Title Case line followed by bullet)
    # The "Next Section" looks like: \n[A-Z][a-z]+... \n •
    # or just \n[A-Z][a-z]+... \n
    
    regex = r"(?i)" + header_group + r"[.:\s-]+(.*?)(\n\s*[A-Z][a-z]+[a-z ]+\n\s*•|\n\s*[A-Z]{3,}|\Z)"
    
    matches = list(re.finditer(regex, text, re.DOTALL))
    
    best_content = ""
    
    for match in matches:
        content = match.group(1).strip()
        
        # Cleaning
        # Remove "System •" or "•"
        content = re.sub(r"^System\s*[•\-]?\s*", "", content, flags=re.IGNORECASE)
        content = re.sub(r"^[•\-]\s*", "", content)
        content = content.replace("\n", " ").strip()
        
        if len(content) > 10:
            # If we found multiple sections (e.g. Stomach AND Abdomen), we should concatenate them?
            # Allen's often has "Stomach" and "Abdomen" separate.
            # We should append them.
            if best_content:
                best_content += " " + content
            else:
                best_content = content
                
    return best_content if len(best_content) > 5 else None

def fill_missing_v3(json_path, pdf_path):
    print("Loading data...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    try:
        reader = pypdf.PdfReader(pdf_path)
        full_text = ""
        # Skip first 10 pages of TOC to speed up and reduce false positives?
        # Actually better to read all and filter.
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    # Map boundaries
    keys = list(data.keys())
    boundaries = get_remedy_boundaries(full_text, set(keys))
    
    # Build range dict
    remedy_ranges = {}
    for i in range(len(boundaries) - 1):
        rem_key, start = boundaries[i]
        next_key, end = boundaries[i+1]
        remedy_ranges[rem_key] = (start, end)
        
    updates = 0
    
    print("Extracting...")
    
    for key, entry in data.items():
        need_gastro = not entry.get("gastro intestinal system") or entry.get("gastro intestinal system") in ["System •", "", "System"]
        need_cardio = not entry.get("cardio vascular system") or entry.get("cardio vascular system") in ["System •", "", "System"]
        
        if not (need_gastro or need_cardio):
            continue
            
        if key not in remedy_ranges:
            # print(f"Skipping {key} (not found in PDF body)")
            continue
            
        start, end = remedy_ranges[key]
        chunk = full_text[start:end]
        
        if need_gastro:
            val = extract_section_content(chunk, "Gastro")
            if val:
                entry["gastro intestinal system"] = val
                print(f"[+] {key} Gastro: {val[:40]}...")
                updates += 1
                
        if need_cardio:
            val = extract_section_content(chunk, "Cardio")
            if val:
                entry["cardio vascular system"] = val
                print(f"[+] {key} Cardio: {val[:40]}...")
                updates += 1

    if updates:
        print(f"Total updates: {updates}")
        shutil.copy(json_path, json_path + ".bak_v3")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Updated JSON.")
    else:
        print("No updates.")

if __name__ == "__main__":
    json_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\app\medicines\allens_keynotes.json"
    pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"
    fill_missing_v3(json_path, pdf_path)
