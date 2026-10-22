from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];D=R/'build/movie-audition'
p=R/'audio-bank/movie-reactions-selection.json';old=json.loads(p.read_text(encoding='utf8'));new=json.loads((D/'expansion-candidates.json').read_text(encoding='utf8'))
new=[r for r in new if r['file'] not in ['good-46.wav','good-48.wav','bad-40.wav','bad-45.wav']]
# Keep the short opening reaction of the longer monologue.
for r in new:
 if r['file']=='bad-44.wav':r['trimEndSeconds']=1.7;r['text']='Ça ne va plus du tout…'
 if r['file']=='good-45.wav':r['text']='Et bonjour la classe ! On va s’éclater ! Pourquoi ? Parce que j’ai une jeunesse de retard !'
 if r['file']=='good-49.wav':r['text']='La même chose que chaque nuit, Minus : tenter de conquérir le monde !'
 if r['file']=='bad-47.wav':r['text']='Ça va, mon grand ? — J’ai connu mieux.'
 if r['file']=='good-44.wav':r['text']='Absolument !'
 if r['file']=='bad-41.wav':r['text']='… Je vois pas en quoi c’est une bonne nouvelle, mais c’est ça.'
 r['verification']='Public soundboard caption and source metadata cross-checked with local speech recognition; transcription retained in expansion audit. Human listening review pending.'
assert len(new)==16
(D/'pre-expansion-hashes.json').write_text(json.dumps({r['file']:hashlib.sha256((D/r['file']).read_bytes()).hexdigest() for r in old},indent=2))
p.write_text(json.dumps(old+new,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
f=R/'build/finalize-expanded-movie-bank.py';s=f.read_text(encoding='utf8').replace('private 60-clip bank','private reaction bank')
s=s.replace('page+=\'\'.join',"totals=collections.Counter(r['outcome'] for r in records)\npage=page.replace('72 extraits',f'{len(records)} extraits').replace('36 bonnes réponses · 36 mauvaises réponses · 62 français · 8 anglais · 2 japonais.',f\"{totals['good']} bonnes réponses · {totals['bad']} mauvaises réponses · {counts['fr']} français · {counts['en']} anglais · {counts['ja']} japonais.\").replace('Voix et langues originales.','Dialogues de films et séries ; langue de chaque extrait conservée.').replace('Le passage burgonde incertain a été remplacé par une autre réplique de Kaamelott, sur la magie. Les extraits précédemment appréciés sont conservés.','Les ajouts récents sont à écouter et à annoter ; les décisions précédentes sont conservées.')\npage+=''.join")
s=s.replace("(D/'credits.html').write_text(page", "page=page.replace('>72 extraits</span>',f'>{len(records)} extraits</span>')\n(D/'credits.html').write_text(page")
f.write_text(s,encoding='utf8')
print('Appended',len(new),'candidates; preserved',len(old),'existing selections.')
