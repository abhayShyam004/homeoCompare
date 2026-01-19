import json
import os

def check_missing_systems(json_path):
    print(f"Checking {json_path} for missing systems...", flush=True)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    missing_gastro = []
    missing_cardio = []

    print(f"Total entries: {len(data)}")

    for key, entry in data.items():
        # Check Gastro Intestinal System
        if not entry.get("gastro intestinal system"):
             missing_gastro.append(key)
        
        # Check Cardio Vascular System
        if not entry.get("cardio vascular system"):
            missing_cardio.append(key)

    print("\n=== Remedies with EMPTY 'gastro intestinal system' ===")
    for m in missing_gastro:
        print(m)
    
    print(f"\nTotal missing Gastro: {len(missing_gastro)}")

    print("\n=== Remedies with EMPTY 'cardio vascular system' ===")
    for m in missing_cardio:
        print(m)
        
    print(f"\nTotal missing Cardio: {len(missing_cardio)}")

if __name__ == "__main__":
    json_path = r"b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\app\allens_keynotes.json"
    check_missing_systems(json_path)
