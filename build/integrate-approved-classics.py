from pathlib import Path
import json,shutil,hashlib
R=Path.cwd();D=R/'build/movie-audition';C=D/'expanded-sources';S=R/'build/classic-audio';p=R/'audio-bank/movie-reactions-selection.json';old=json.loads(p.read_text(encoding='utf8'));candidates=json.loads((R/'audio-bank/classic-reactions-candidates.json').read_text(encoding='utf8'))
(D/'pre-classic-integration-hashes.json').write_text(json.dumps({r['file']:hashlib.sha256((D/r['file']).read_bytes()).hexdigest() for r in old},indent=2),encoding='utf8')
for r in candidates:
 r['selectionReview']='Full shortlist approved by user, 2026-10-15.'
 r['status']='approved_audio_pending'
 if r['id'] in ['bond-perfect','bond-congratulations']:
  filename='good-38.wav' if r['id']=='bond-perfect' else 'good-39.wav'
  assert filename not in {o['file'] for o in old}
  shutil.copyfile(S/'sources'/(r['id']+'.source'),C/(filename+'.source'))
  shutil.copyfile(S/'sources'/(r['id']+'.wav'),C/(filename+'.wav'))
  clip={k:r[k] for k in ['outcome','language','film','text','sourceUrl','downloadUrl','trimStartSeconds','trimEndSeconds','sourceDurationSeconds']}
  clip.update(file=filename,voice=r['sourceCredit'],sourceType='original_film_dialogue',usage='Private on-device audition; no redistribution permission asserted',verification='Public scene metadata, decoded source audio and speech recognition; selection approved by user.',audience='all')
  old.append(clip);r['bankFile']=filename;r['status']='added_to_bank';r['reviewNote']='User approved the full shortlist. Normalized cut integrated into the private reaction bank.'
  if r['id']=='bond-congratulations':r['voice']='Bernard Lee / M'
(R/'audio-bank/classic-reactions-candidates.json').write_text(json.dumps(candidates,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
f=R/'build/finalize-expanded-movie-bank.py';s=f.read_text(encoding='utf8')
s=s.replace("if r.get('trimEndSeconds'):filters='atrim=end='+str(r['trimEndSeconds'])+',asetpts=PTS-STARTPTS,'+filters", "if r.get('trimStartSeconds') or r.get('trimEndSeconds'):\n  trim=[]\n  if r.get('trimStartSeconds'):trim.append('start='+str(r['trimStartSeconds']))\n  if r.get('trimEndSeconds'):trim.append('end='+str(r['trimEndSeconds']))\n  filters='atrim='+':'.join(trim)+',asetpts=PTS-STARTPTS,'+filters")
f.write_text(s,encoding='utf8')
print('Integrated 2 Bond clips; recorded approval of all 21 shortlisted selections.')
