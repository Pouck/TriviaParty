import json,pathlib,re,sys
sys.stdout.reconfigure(encoding='utf8')
rows=json.loads(pathlib.Path('build/movie-audition/all-bleeps.json').read_text(encoding='utf8'));used={r['downloadUrl'] for r in json.loads(pathlib.Path('audio-bank/movie-reactions-selection.json').read_text(encoding='utf8'))}
print('CATALOG',len(rows))
pattern=re.compile(r'bravo|excellent|g[ée]ni|magnifique|bien jou|parfait|[ée]patant|r[ée]ussi|gagn|formidable|imb[ée]cile|rat[ée]|perdu|n.?importe|compr|lament|pas possible|connerie|sais pas|nul|[ée]chec|faux|intelligen|merveille|impression|progr[èe]s',re.I)
for r in rows:
 if r.get('sound') in used or 'tontons' in r.get('source_name','').lower():continue
 if pattern.search(r['name']):print(json.dumps({k:r.get(k) for k in ['name_unique','name','source_name','actor_name','speaker_name','lang']},ensure_ascii=False))
