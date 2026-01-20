import pdfplumber
import json
import re

def extract_relationships(pdf_path, output_json):
    relationships = []
    
    # Common headers mapping
    # The PDF likely has columns: Remedy, Complements, Follows Well, Antidotes, Inimical, Duration
    
    current_remedy = {}
    
    print(f"Opening {pdf_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                print(f"Processing page {i+1}...")
                tables = page.extract_tables()
                
                for table in tables:
                    for row in table:
                        # Clean row data (remove Nones and newlines)
                        cleaned_row = [cell.replace('\n', ' ').strip() if cell else '' for cell in row]
                        
                        # Heuristic: Check if this looks like a data row
                        # Usually the first column is the Remedy name
                        if not cleaned_row or not cleaned_row[0]:
                            continue
                            
                        # Skip header rows (detect common keywords)
                        if "Remedies" in cleaned_row[0] or "Duration" in cleaned_row[-1]:
                            continue

                        # Assuming standard 6-column layout from Gibson Miller
                        # 0: Remedy, 1: Complements, 2: Remedies that Follow, 3: Antidotes, 4: Inimical, 5: Duration
                        if len(cleaned_row) >= 5:
                            entry = {
                                "remedy": cleaned_row[0],
                                "complements": cleaned_row[1] if len(cleaned_row) > 1 else "",
                                "follows": cleaned_row[2] if len(cleaned_row) > 2 else "",
                                "antidotes": cleaned_row[3] if len(cleaned_row) > 3 else "",
                                "inimical": cleaned_row[4] if len(cleaned_row) > 4 else "",
                                "duration": cleaned_row[5] if len(cleaned_row) > 5 else ""
                            }
                            relationships.append(entry)
        
        # Save to JSON
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=4)
            
        print(f"Successfully extracted {len(relationships)} entries to {output_json}")
        
    except Exception as e:
        print(f"Error extracting PDF: {e}")

if __name__ == "__main__":
    extract_relationships("relationship-of-remedies-dr-rgibson-miller.pdf", "app/medicines/remedy_relationships.json")
