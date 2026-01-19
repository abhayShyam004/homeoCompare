import pypdf

pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"

def extract_zincum():
    print("Extracting last 20 pages for Zincum...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        num_pages = len(reader.pages)
        start_page = max(0, num_pages - 20)
        
        full_text = ""
        for i in range(start_page, num_pages):
            full_text += reader.pages[i].extract_text() + "\n"
            
        # Find start of ZINCUM
        start_marker = "ZINCUM METALLICUM"
        start_idx = full_text.find(start_marker)
        if start_idx == -1:
            # Try just ZINCUM
            start_idx = full_text.find("ZINCUM")
            
        if start_idx != -1:
            print(f"Found Zincum at index {start_idx}")
            with open("zincum_dump.txt", "w", encoding="utf-8") as f:
                f.write(full_text[start_idx:])
            print("Wrote to zincum_dump.txt")
        else:
            print("Could not find ZINCUM in last 20 pages.")
            with open("zincum_debug.txt", "w", encoding="utf-8") as f:
                f.write(full_text[-5000:])
            print("Wrote debug dump to zincum_debug.txt")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_zincum()
