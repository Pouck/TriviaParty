from pathlib import Path
import json, zipfile, csv

root = Path('package-examples/geographie-2026-10-10')
audit = {item['questionId']: item for item in json.loads((root/'verification-images.json').read_text(encoding='utf-8')) if 'labels' in item}
rows = []
for archive in sorted(root.glob('*.zip')):
    if 'capitales' in archive.name:
        continue
    with zipfile.ZipFile(archive) as z:
        contents = {info.filename: z.read(info) for info in z.infolist()}
    for name, data in list(contents.items()):
        if not name.startswith('question-bank/'):
            continue
        category = json.loads(data)
        for q in category['questions']:
            variants = []
            for letter, location in audit[q['id']]['labels'].items():
                if any(word in location for word in ['ambigu', 'supposée', 'approximative', 'territoire français']):
                    continue
                # Quoted names avoid gender/article mistakes and work for countries and US states.
                prompt = f'Quelle lettre indique « {location} » sur la carte ?'
                variants.append({'prompt': prompt, 'correctOptionIndex': 'ABCD'.index(letter)})
                rows.append([category['category'], q['id'], q['imageUrl'], prompt, letter, location])
            q['randomVariants'] = variants
        encoded = (json.dumps(category, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
        contents[name] = encoded
        manifest = json.loads(contents['game.json'])
        source = root/'sources'/manifest['id']/name
        source.write_bytes(encoded)
    temporary = archive.with_suffix('.tmp')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in contents.items():
            z.writestr(name, data)
    temporary.replace(archive)
with (root/'VARIANTES-CARTES.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Catégorie', 'Question', 'Image', 'Texte', 'Lettre correcte', 'Lieu'])
    writer.writerows(rows)
print(f'{len(rows)} variantes pour {len(audit)} cartes ; ZIP et sources mis à jour.')
