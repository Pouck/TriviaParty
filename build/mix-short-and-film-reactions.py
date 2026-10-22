from pathlib import Path
import json,hashlib
R=Path.cwd();p=R/'audio-bank/movie-reactions-selection.json';rows=json.loads(p.read_text(encoding='utf8'));shorts=json.loads((R/'audio-bank/reactions.json').read_text(encoding='utf8'))
ids=['good-11.wav','good-04.wav','good-10.wav','good-06.wav','bad-03.wav','bad-07.wav','bad-14.wav','bad-09.wav','bad-12.wav','bad-11.wav']
assert len(rows)==90
for name in ids:
 assert name not in {r['file'] for r in rows}
 r=dict(next(r for r in shorts if r['file']==name));asset=R/'audio-bank/clips'/name
 assert hashlib.sha256(asset.read_bytes()).hexdigest()==r['sha256']
 r.update(preparedAsset='audio-bank/clips/'+name,film='Réactions courtes (voix humaines)',audience='all',verification='Existing licensed human recording; copied without changes for mixing with approved dialogue.',usage='Licensed human recording; retain attribution and license.',selectionReview='User requested short spoken reactions mixed with film dialogue, 2026-10-15.')
 rows.append(r)
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
f=R/'build/finalize-expanded-movie-bank.py';s=f.read_text(encoding='utf8').replace('import sys,json,subprocess,wave,hashlib,html,collections','import sys,json,subprocess,wave,hashlib,html,collections,shutil')
s=s.replace(' subprocess.run(command,check=True,capture_output=True)'," if r.get('preparedAsset'):\n  source=(ROOT/r['preparedAsset']).resolve()\n  assert source.is_relative_to((ROOT/'audio-bank/clips').resolve())\n  assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sha256']\n  shutil.copyfile(source,dest)\n else:subprocess.run(command,check=True,capture_output=True)")
s=s.replace('Réactions cinéma — 72 extraits','Réactions vocales — 72 extraits').replace('Dialogues de films et séries ; langue de chaque extrait conservée.','Répliques de films et séries, mêlées à des réactions humaines courtes ; langue de chaque extrait conservée.')
s=s.replace("page+=\"\"\"</main><script>"," if r.get('license'):\n  credit=f\"<p class='meta'>Licence : <a href='{html.escape(r['licenseUrl'],quote=True)}'>{html.escape(r['license'])}</a> · {html.escape(r.get('attribution',r['voice']))}<br>{html.escape(r.get('changes',''))}</p>\"\n  page=page.rsplit('</article>',1)[0]+credit+'</article>'\npage+=\"\"\"</main><script>")
f.write_text(s,encoding='utf8')
print('Selected 10 brief French reactions; total 100 clips, 50 for each outcome. Existing licenses retained.')
