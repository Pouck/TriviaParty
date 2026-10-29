"""Prepare the user's reviewed private recordings; original downloads remain intact."""
import argparse
import concurrent.futures
import difflib
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
import wave
import shutil
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'build/audio-tools'))
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
OUT = ROOT / 'build/reviewed-audio-20261024'
ALIGN = OUT / 'alignment'
WHISPER = ROOT / 'build/movie-audition/whisper-bin/Release/whisper-cli.exe'
MODEL = ROOT / 'build/movie-audition/ggml-small.bin'
REVIEW = Path.home() / 'Downloads/audio-clips-review (1).json'


def norm(text):
    text = re.sub(r'\(\d+\)\s*$', '', text)
    text = ''.join(c for c in unicodedata.normalize('NFD', text.lower()) if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[a-z0-9]+', text))


def source(clip):
    path = (ROOT / 'build/downloaded-clips-review' / clip['src']).resolve()
    assert path.is_relative_to(ROOT / 'build'), path
    assert hashlib.sha256(path.read_bytes()).hexdigest() == clip['sha256'], clip['id']
    return path


def transcribe(clip, use_base=False):
    prefix = ALIGN / (clip['id'] + ('-base' if use_base else ''))
    result = prefix.with_suffix('.json')
    if not result.exists():
        wav = (ALIGN / clip['id']).with_suffix('.wav')
        subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(source(clip)),
            '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)], check=True)
        subprocess.run([str(WHISPER), '-m', str(MODEL.with_name('ggml-base.bin') if use_base else MODEL), '-f', str(wav), '-l', 'fr', '-mc','0',
            '--prompt', norm(clip['text']),
            '-oj', '-ml', '1', '-sow', '-of', str(prefix), '-t', '4', '-np'],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    result_data = json.loads(result.read_text(encoding='utf-8'))
    print(clip['number'], 'transcribed:', ' '.join(s['text'].strip() for s in result_data['transcription']), flush=True)
    return clip['id']


def align(clip):
    full = norm(clip['text']) == norm(clip['review']['trimText'])
    if full:
        return dict(start=0, end=clip['durationSeconds'], score=1, fullPhrase=True)
    prefix = ALIGN / clip['id']
    alternate = Path(str(prefix) + '-base.json')
    transcript = json.loads((alternate if alternate.exists() else prefix.with_suffix('.json')).read_text(encoding='utf-8'))
    words = [(word, part['offsets']['from']/1000, part['offsets']['to']/1000)
        for part in transcript['transcription'] for word in norm(part['text']).split()]
    target = norm(clip['review']['trimText'])
    best = (0, 0, 0)
    for start in range(len(words)):
        for end in range(start+1, len(words)+1):
            text = ' '.join(w[0] for w in words[start:end])
            score = difflib.SequenceMatcher(None, target, text).ratio()
            if score > best[0]:
                best = (score, start, end)
    score, first, last = best
    assert score >= .66, (clip['number'], score, target)
    start = max(0, words[first][1] - .055)
    end = min(clip['durationSeconds'], words[last-1][2] + .055)
    # Preserve natural trailing speech when the requested phrase goes to the end.
    if last == len(words):
        end = clip['durationSeconds']
    if norm(clip['text']).startswith(target):
        start = 0
    return dict(start=round(start,3), end=round(end,3), score=round(score,3), fullPhrase=False,
        recognized=' '.join(w[0] for w in words[first:last]))


def build_bank(data):
    bounds = {}
    for clip in data['clips']:
        if clip['review']['decision'] == 'trim':
            bounds[clip['id']] = align(clip)
    (OUT/'trim-boundaries.json').write_text(json.dumps(bounds,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.align_only:
        for clip in data['clips']:
            if clip['id'] in bounds:
                print(clip['number'],clip['review']['trimText'],bounds[clip['id']],flush=True)
        return
    bank = OUT/'bank'
    processed = OUT/'processed'
    bank.mkdir(exist_ok=True);processed.mkdir(exist_ok=True)
    rows=[];counters={'good':0,'bad':0};included=[]
    for clip in data['clips']:
        review=clip['review']
        if review['decision']=='reject' or clip['number']==44:
            continue
        assert review['usage'] in ('correct','incorrect','both'),clip['id']
        assert review['audience'] in ('yes','no','unsure'),clip['id']
        cut=bounds.get(clip['id'],dict(start=0,end=clip['durationSeconds'],fullPhrase=True))
        interval=f'atrim=start={cut["start"]}' + (f':end={cut["end"]}' if cut['end'] is not None else '')
        filters=[interval,'asetpts=PTS-STARTPTS']
        if review['decision']=='trim' and cut['fullPhrase']:
            edge='silenceremove=start_periods=1:start_duration=0.02:start_threshold=-55dB'
            filters += [edge,'areverse',edge,'areverse']
        filters += ['loudnorm=I=-18:TP=-2:LRA=11','aresample=44100','afade=t=in:d=0.004',
            'areverse','afade=t=in:d=0.008','areverse','adelay=220:all=1','apad=pad_dur=0.10']
        audio=processed/(clip['id']+'.wav')
        settings=hashlib.sha256((clip['sha256']+'|'+','.join(filters)).encode()).hexdigest()
        stamp=audio.with_suffix('.settings')
        if not audio.exists() or not stamp.exists() or stamp.read_text()!=settings:
            subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(source(clip)),
                '-af',','.join(filters),'-ar','44100','-ac','1','-c:a','pcm_s16le',str(audio)],check=True)
            stamp.write_text(settings)
        with wave.open(str(audio),'rb') as wav:
            assert wav.getnchannels()==1 and wav.getframerate()==44100
            duration=wav.getnframes()/wav.getframerate()
        assert 0.15<duration<55,clip['id']
        assert audio.stat().st_size<5_000_000
        included.append(clip['id'])
        for outcome in (['good','bad'] if review['usage']=='both' else ['good'] if review['usage']=='correct' else ['bad']):
            counters[outcome]+=1
            filename=f'{outcome}-{counters[outcome]:03}.wav'
            shutil.copyfile(audio,bank/filename)
            rows.append(dict(file=filename,outcome=outcome,voice='user-recording:'+clip['id'],
                film='',text=review['trimText'].strip() if review['decision']=='trim' else clip['text'],
                audience={'yes':'all','no':'mature','unsure':'unreviewed'}[review['audience']],
                sourceId=clip['id'],sourceSha256=clip['sha256'],sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),
                durationSeconds=round(duration,3),reviewDecision=review['decision'],
                trim=cut if review['decision']=='trim' else None,
                source='User-provided recording; original film and speaker not verified'))
    (bank/'reactions.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (bank/'credits.html').write_text('<meta charset="utf-8"><title>Reviewed recordings</title><h1>Private reviewed recordings</h1><p>User-provided recordings. Original voices preserved; source film and speaker unverified.</p><ul>'+''.join('<li>'+html.escape(r['file']+' — '+r['text'])+'</li>' for r in rows)+'</ul>',encoding='utf-8')
    report=dict(reviewExport=data['exportedAt'],uniqueClips=len(included),outcomeEntries=len(rows),
        counts=counters,rejected=[c['id'] for c in data['clips'] if c['review']['decision']=='reject'],
        omitted=[dict(id=data['clips'][43]['id'],reason='User requested leaving incomplete clip 44 out')],
        trimmed=list(bounds),allAudiences=sum(r['audience']=='all' for r in rows))
    (OUT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (ROOT/'audio-bank/reviewed-clips-selection.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--transcribe', action='store_true')
    parser.add_argument('--align-only', action='store_true')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--recheck', type=int, nargs='+')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    ALIGN.mkdir(exist_ok=True)
    data = json.loads(REVIEW.read_text(encoding='utf-8-sig'))
    (ROOT / 'review-backups/audio-clips-review-2026-10-24-1748-raw.json').write_bytes(REVIEW.read_bytes())
    clips = [c for c in data['clips'] if c['review']['decision'] == 'trim'
        and norm(c['text']) != norm(c['review']['trimText'])]
    for clip in data['clips']:
        source(clip)
    print(f'All {len(data["clips"])} source hashes verified; {len(clips)} requested speech subsets need word alignment.', flush=True)
    if args.transcribe:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            list(executor.map(transcribe, clips))
    if args.recheck:
        for clip in data['clips']:
            if clip['number'] in args.recheck:
                transcribe(clip, use_base=True)
    if args.align_only or args.build:
        build_bank(data)
