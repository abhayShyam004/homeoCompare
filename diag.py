
import sys
import os

try:
    import pypdf
    print("pypdf is installed")
except ImportError:
    print("pypdf is NOT installed")

try:
    pdf_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\Allen's KeyNotes_With Repertorial Index_10th Edition.pdf"
    if os.path.exists(pdf_path):
        print(f"PDF exists at {pdf_path}")
    else:
        print(f"PDF NOT found at {pdf_path}")
except Exception as e:
    print(f"Error checking file: {e}")
