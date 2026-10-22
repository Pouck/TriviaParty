from pathlib import Path
import json,html,wave,hashlib,collections
R=Path.cwd();D=R/'build/classic-audio';rows=json.loads((D/'audit.json').read_text(encoding='utf8'))
rows=[r for r in rows if r['id']!='bond-shocking']
for r in rows:
 r.pop('error',None)
 if r['id'].startswith('classic-'):
  r['audioStatus']='source_download_forbidden';r['status']='source_found_audio_pending';r['reviewNote']='Source page lists an audio excerpt; automated download returned HTTP 403. Do not enable before listening and verifying the speaker.'
 else:
  r['audioStatus']='local_audition';r['status']='prepared_listening_review_pending';r['trimStartSeconds']=4.4 if r['id']=='bond-perfect' else 14.0;r['trimEndSeconds']=8 if r['id']=='bond-perfect' else 16.7
  r['reviewNote']='Short cut decoded and checked with speech recognition; human listening review pending.'
  with wave.open(str(D/r['file'])) as w:r['durationSeconds']=round(w.getnframes()/w.getframerate(),3)
  r['sha256']=hashlib.sha256((D/r['file']).read_bytes()).hexdigest()
 if r['id']=='classic-443401':r['text']='Tu m’impressionnes. C’est vrai. Même quand tu es tendre, tu m’impressionnes.';r['reviewNote']+=' Proposed middle excerpt; exact cut pending.'
 if r['id']=='classic-434148':r['text']='Réfléchis deux secondes !';r['reviewNote']+=' Proposed closing excerpt; exact cut pending.'
 if r['id']=='classic-429856':r['text']='Très bien.';r['reviewNote']+=' Proposed opening excerpt; exact cut pending.'
 if r['id']=='classic-396735':r['text']='Très drôle.';r['reviewNote']+=' Proposed closing excerpt; exact cut and speaker pending.'
 if r['id']=='classic-511412':r['text']='Ah, je ne savais pas. — Savoir n’est pas le métier de tout le monde.'
 if r['id']=='classic-447131':r['text']='Quand tu dis bien sûr, tu sais pas.';r['reviewNote']+=' Multi-speaker source: attribution of this phrase must be confirmed.'
 if r['id']=='classic-449576':r['reviewNote']+=' Multi-speaker exchange: isolate Ventura before activation.'
 if r['id']=='classic-444082':r['reviewNote']+=' Insult; audience classification pending.'
 if r['id']=='bond-perfect':r['text']='Perfect. Cheers. — Cheers.';r['sourceCredit']='Sean Connery / James Bond; Charles Gray / Henderson (second Cheers)'
rows += [dict(id='classic-bourvil-corniaud',outcome='bad',language='fr',film='Le Corniaud (1965)',requestedActor='Bourvil',sourceCredit='Bourvil / Antoine Maréchal',text='Bah maintenant, elle va marcher beaucoup moins bien, forcément.',sourceUrl='https://zonesons.com/films-de-comedie/le-corniaud-1965/422841',alternateSourceUrl='https://www.youtube.com/watch?v=FNVQg0DBLwo',priority='strong',audience='unreviewed',status='reference_only',audioStatus='source_found',reviewNote='Strong failure reaction; clip not downloaded.'),dict(id='bond-shocking-reference',outcome='bad',language='en',film='Goldfinger (1964)',requestedActor='Sean Connery',sourceCredit='Sean Connery / James Bond',text='Shocking! Positively shocking!',sourceUrl='https://www.youtube.com/watch?v=LM4f_Ghx-o0',priority='strong',audience='unreviewed',status='reference_only',audioStatus='source_found',reviewNote='Clip.Cafe download rejected: actual audio differed from caption. Use the linked scene as a reference; no audition file enabled.')]
manifest=R/'audio-bank/classic-reactions-candidates.json';manifest.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
labels={'strong':'Prioritaire','optional':'Option : ton à juger','edit_needed':'Découpe à vérifier','speaker_check':'Locuteur à confirmer'}
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Réactions — cinéma classique</title><style>body{max-width:1100px;margin:30px auto;padding:0 18px;background:#101827;color:#eef4ff;font:18px system-ui}a{color:#9dd6ff}select{font:inherit;padding:10px;margin:6px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:16px}article{background:#21324b;border-radius:12px;padding:18px;border-left:6px solid #ff8989}article.good{border-color:#78dda2}article[hidden]{display:none}h2{font-size:22px}audio{width:100%}.note{font-size:15px;color:#c1cde2}blockquote{font-size:21px;margin:16px 0}</style><h1>Réactions — cinéma classique et James Bond</h1><p>21 pistes : 18 françaises et 3 James Bond. Deux fichiers locaux à écouter ; les autres sont des références sourcées. Aucun ajout activé dans la banque du jeu.</p><p>Les téléchargements de ZoneSons renvoient HTTP 403. Les pages sources restent liées ci-dessous. Les découpes proposées et les échanges à plusieurs voix doivent être vérifiés à l’écoute.</p><select id="outcome"><option value="">Tous les résultats</option><option value="good">Bonne réponse</option><option value="bad">Mauvaise réponse</option></select><select id="priority"><option value="">Toutes les pistes</option><option value="strong">Prioritaires</option><option value="local">Audio local disponible</option></select><main>'''
for r in rows:
 local=r['audioStatus']=='local_audition';page+=f'<article class="{r["outcome"]}" data-priority="{r["priority"]}" data-local="{str(local).lower()}"><h2>{html.escape(r["requestedActor"])}</h2><p>{html.escape(r["film"])} · {"Bonne réponse" if r["outcome"]=="good" else "Mauvaise réponse"}</p><blockquote>{html.escape(r["text"])}</blockquote><p>{labels[r["priority"]]}</p><p class="note">Crédit source : {html.escape(r["sourceCredit"])}</p>'
 if local:page+=f'<audio controls preload="none" src="./{r["file"]}"></audio>'
 page+=f'<p><a href="{html.escape(r["sourceUrl"],quote=True)}">Ouvrir la source</a></p><p class="note">{html.escape(r["reviewNote"])}</p></article>'
page+='''</main><script>const cards=[...document.querySelectorAll('article')],o=document.querySelector('#outcome'),p=document.querySelector('#priority');function filter(){cards.forEach(c=>c.hidden=!!((o.value&&!c.classList.contains(o.value))||(p.value==='strong'&&c.dataset.priority!=='strong')||(p.value==='local'&&c.dataset.local!=='true')))}o.oninput=p.oninput=filter;document.querySelectorAll('audio').forEach(a=>a.onplay=()=>document.querySelectorAll('audio').forEach(b=>{if(a!==b)b.pause()}))</script></html>'''
(D/'index.html').write_text(page,encoding='utf8')
md='''# Pistes cinéma classique et James Bond — 15 octobre 2026

21 pistes sourcées, dont 2 découpes audio locales pour audition. Elles restent séparées des 88 réactions préparées : aucune sélection ni annotation existante n’a changé.

Écouter / consulter : [page de sélection](../build/classic-audio/index.html). Métadonnées : [classic-reactions-candidates.json](classic-reactions-candidates.json).

Les fichiers de ZoneSons n’ont pas pu être récupérés (HTTP 403), même après navigation normale avec cookies et référent. Les liens sont des références, pas une promesse de fichier disponible. Les deux extraits Bond ont été décodés et confrontés à la reconnaissance vocale, mais attendent une écoute humaine. Une source Goldfinger dont le fichier ne correspondait pas à la légende a été rejetée.

| Acteur | Résultat envisagé | Extrait proposé | Œuvre | État |
| --- | --- | --- | --- | --- |
'''
for r in rows:md+='| '+ ' | '.join([r['requestedActor'],'Bonne' if r['outcome']=='good' else 'Mauvaise','['+r['text'].replace('|','/')+']('+r['sourceUrl']+')',r['film'],labels[r['priority']]+(' ; fichier local' if r['audioStatus']=='local_audition' else ' ; référence')])+' |\n'
md+='''
## Couverture et suites de recherche

Les pistes couvrent Bourvil, Gabin, Ventura, de Funès, Belmondo, Noiret, Bardot, Girardot, Auteuil, Blier, Depardieu, Richard, Rochefort, Serrault, Adjani et Deneuve, plus Connery et Bernard Lee dans Bond. Une présence sur une page d’acteur ne confirme pas à elle seule chaque voix d’un échange : les cas ambigus sont indiqués dans les métadonnées.

Aucun extrait court suffisamment convaincant avec audio vérifiable n’a encore été retenu pour Françoise Fabian, Jeanne Moreau, Romy Schneider, Emmanuelle Béart, Juliette Binoche, Sandrine Bonnaire et Carole Bouquet. Ne pas combler ces absences par des répliques attribuées de mémoire ou des phrases sans rapport avec une réponse de quiz.

Pour la sélection finale : privilégier 1 à 5 secondes, une réaction compréhensible sans contexte, une seule voix clairement identifiée et un sens cohérent avec bonne/mauvaise réponse. Toutes les nouvelles pistes restent à annoter pour le filtre tout public. Les médias sont réservés à l’audition privée ; aucun droit de redistribution n’est affirmé.
'''
(R/'audio-bank/CLASSIC-REACTIONS.md').write_text(md,encoding='utf8')
print('Saved',len(rows),'candidates;',sum(r['audioStatus']=='local_audition' for r in rows),'local audition files;',collections.Counter(r['priority'] for r in rows))
for r in rows:print(r['id'],r['film'])
