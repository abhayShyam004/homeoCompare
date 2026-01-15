import json
import os
from pathlib import Path

medicines_dir = Path(r'b:\Documents\vscode\New folder\DjangoProject\medicineMedica\medica\medicomp\app\medicines')

# Fields that should stay at top level
keep_at_top = {'name', 'symptoms'}

# Track stats
fixed_count = 0
skipped_count = 0
errors = []

for json_file in sorted(medicines_dir.glob('*.json')):
    if json_file.name == 'allens_keynotes.json' or json_file.name == 'links.html':
        continue
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        symptoms = data.get('symptoms', {})
        fields_moved = []
        
        # Move top-level fields into symptoms
        for key in list(data.keys()):
            if key not in keep_at_top:
                value = data.pop(key)
                if value:  # Only move non-empty values
                    symptoms[key] = value
                    fields_moved.append(key)
        
        if fields_moved:
            data['symptoms'] = symptoms
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            fixed_count += 1
            print(f'Fixed: {json_file.name} - moved {len(fields_moved)} fields')
        else:
            skipped_count += 1
            
    except Exception as e:
        errors.append(f'{json_file.name}: {e}')

print(f'\n=== Migration Complete ===')
print(f'Fixed: {fixed_count} files')
print(f'Already OK: {skipped_count} files')
if errors:
    print(f'Errors: {len(errors)}')
    for e in errors[:5]:
        print(f'  - {e}')
