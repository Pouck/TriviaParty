from __future__ import annotations

import hashlib
import html
import json
import mimetypes
import shutil
from datetime import date, datetime
from pathlib import Path

ROOT = Path.cwd()
DOWNLOADS = Path(r"C:\Users\pierr\Downloads")
TODAY = date.today().strftime("%Y%m%d")
BATCH = ROOT / "build" / f"downloaded-clips-{TODAY}"
OUT = ROOT / "build" / "downloaded-clips-review"
SUPPORTED = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac", ".opus", ".webm"}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def duration(path: Path) -> float | None:
    if path.suffix.lower() == ".wav":
        try:
            import wave
            with wave.open(str(path), "rb") as wav:
                return round(wav.getnframes() / wav.getframerate(), 3)
        except (OSError, wave.Error, ZeroDivisionError):
            pass
    return None


def import_today() -> tuple[int, list[str]]:
    BATCH.mkdir(parents=True, exist_ok=True)
    media = BATCH / "originals"
    media.mkdir(exist_ok=True)
    previous: dict[str, str] = {}
    for manifest_path in (ROOT / "build").glob("downloaded-clips-*/manifest.json"):
        if manifest_path.parent == BATCH:
            continue
        try:
            for clip in json.loads(manifest_path.read_text(encoding="utf-8")).get("clips", []):
                previous[clip["sha256"]] = clip.get("originalName", clip.get("file", "previous import"))
        except (OSError, ValueError, KeyError):
            continue

    candidates = sorted(
        (p for p in DOWNLOADS.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED
         and datetime.fromtimestamp(p.stat().st_mtime).date() == date.today()),
        key=lambda p: p.name.casefold(),
    )
    seen: dict[str, str] = {}
    clips: list[dict] = []
    duplicates: list[dict] = []
    previously_imported: list[str] = []
    for path in candidates:
        digest = sha(path)
        if digest in previous:
            previously_imported.append(path.name)
            continue
        if digest in seen:
            duplicates.append({"file": path.name, "duplicateOf": seen[digest]})
            continue
        filename = f"{len(clips) + 1:03d}{path.suffix.lower()}"
        shutil.copy2(path, media / filename)
        seen[digest] = path.name
        clips.append({
            "number": len(clips) + 1,
            "originalName": path.name,
            "file": f"originals/{filename}",
            "sha256": digest,
            "bytes": path.stat().st_size,
            "durationSeconds": duration(path),
            "textFromFilename": path.stem.replace("-", " "),
            "source": "User-provided local download; film and speaker not independently verified",
        })
    manifest = {
        "importedAt": datetime.now().astimezone().isoformat(),
        "sourceDirectory": str(DOWNLOADS),
        "downloadCount": len(candidates),
        "uniqueCount": len(clips),
        "duplicates": duplicates,
        "previouslyImported": previously_imported,
        "clips": clips,
    }
    (BATCH / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(clips), previously_imported


def collect_all() -> list[dict]:
    clips: list[dict] = []
    for manifest_path in sorted((ROOT / "build").glob("downloaded-clips-*/manifest.json")):
        if manifest_path.parent == OUT:
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for item in manifest.get("clips", []):
            original = manifest_path.parent / item["file"]
            if not original.is_file():
                continue
            rel = Path("..") / manifest_path.parent.name / item["file"]
            clips.append({
                "id": f"{manifest_path.parent.name}-{item['number']:03d}",
                "number": len(clips) + 1,
                "batch": manifest_path.parent.name,
                "name": item.get("originalName", Path(item["file"]).name),
                "text": item.get("textFromFilename", Path(item["file"]).stem.replace("-", " ")),
                "src": rel.as_posix(),
                "durationSeconds": item.get("durationSeconds") or duration(original),
                "sha256": item.get("sha256") or sha(original),
            })
    return clips


new_count, duplicates = import_today()
clips = collect_all()
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "manifest.json").write_text(json.dumps({
    "createdAt": datetime.now().astimezone().isoformat(),
    "scope": "All unique clips in the user-provided Downloads imports",
    "count": len(clips),
    "clips": clips,
}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

clip_json = json.dumps(clips, ensure_ascii=False).replace("</", "<\\/")
cards = []
for clip in clips:
    title = html.escape(clip["text"])
    name = html.escape(clip["name"])
    seconds = f"{clip['durationSeconds']:.1f} s" if clip["durationSeconds"] else "duration unknown"
    src = html.escape(clip["src"], quote=True)
    cards.append(f'''<article class="clip" data-id="{html.escape(clip['id'], quote=True)}" data-search="{html.escape((clip['text']+' '+clip['name']+' '+clip['batch']).casefold(), quote=True)}">
<header><span class="number">{clip['number']:03d}</span><div><h2>{title}</h2><small>{name} · {seconds} · {html.escape(clip['batch'])}</small></div></header>
<audio controls preload="none" src="{src}"></audio>
<div class="fields">
<label>Usage<select data-field="usage"><option value="">Choose…</option><option value="correct">Correct answer</option><option value="incorrect">Incorrect answer</option><option value="both">Both</option></select></label>
<label>Suitable for all audiences?<select data-field="audience"><option value="">Choose…</option><option value="yes">Yes</option><option value="no">No</option><option value="unsure">Unsure</option></select></label>
<label>Decision<select data-field="decision"><option value="">Choose…</option><option value="keep">Keep clip</option><option value="reject">Reject clip</option><option value="trim">Needs trimming</option></select></label>
<label class="trim">Text to retain for trimming<input data-field="trimText" type="text" placeholder="Paste the exact dialogue to keep"></label>
</div></article>''')

page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Audio clip review sampler</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101725;color:#eef3ff;font:16px system-ui,sans-serif;max-width:1100px;padding:24px;margin-inline:auto}h1{margin:0 0 8px}.intro{color:#bdcbe0}.toolbar{position:sticky;top:0;background:#101725ee;backdrop-filter:blur(10px);padding:12px 0;z-index:2;display:flex;gap:10px;flex-wrap:wrap}button,input,select{font:inherit;color:inherit;background:#202f44;border:1px solid #526780;border-radius:8px;padding:10px}button{cursor:pointer}#search{flex:1;min-width:220px}.progress{align-self:center;color:#bcd0e8}article{background:#1b293c;border:1px solid #344861;border-radius:14px;padding:18px;margin:14px 0}header{display:flex;gap:14px;align-items:flex-start}.number{font-size:22px;font-weight:700;color:#82c8ff}h2{font-size:19px;margin:0 0 5px;overflow-wrap:anywhere}small{color:#b6c7dc}audio{width:100%;margin:14px 0}.fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:12px}.fields label{display:flex;flex-direction:column;gap:6px;color:#cbd9eb}.fields select,.fields input{width:100%}.trim{grid-column:span 2}@media(max-width:600px){body{padding:14px}.trim{grid-column:auto}}
</style><h1>Audio clip review sampler</h1><p class="intro">Review each unique clip from the imported Downloads batches. Your choices save in this browser. Export a JSON file when finished. For a trim request, select “Needs trimming” and paste the exact words to retain.</p>
<div class="toolbar"><input id="search" type="search" placeholder="Search clips"><button id="playAll">Play visible clips</button><button id="stop">Stop</button><button id="export">Export review</button><button id="import">Load review JSON</button><input id="file" type="file" accept="application/json" hidden><span class="progress" id="progress"></span></div>
<main>''' + "\n".join(cards) + '''</main>
<script>
const clips=CLIP_DATA, key='downloaded-clips-review-20261018';
const articles=[...document.querySelectorAll('article')], audios=articles.map(x=>x.querySelector('audio'));
let saved={};try{saved=JSON.parse(localStorage.getItem(key)||'{}')}catch{}
function apply(){for(const a of articles){const v=saved[a.dataset.id]||{};for(const e of a.querySelectorAll('[data-field]'))if(v[e.dataset.field]!==undefined)e.value=v[e.dataset.field]}update()}
function store(a){const v={};for(const e of a.querySelectorAll('[data-field]'))v[e.dataset.field]=e.value;saved[a.dataset.id]=v;try{localStorage.setItem(key,JSON.stringify(saved))}catch{}update()}
function update(){const decided=Object.values(saved).filter(x=>x.usage||x.audience||x.decision).length;document.querySelector('#progress').textContent=`${decided} / ${clips.length} reviewed`}
articles.forEach(a=>a.querySelectorAll('[data-field]').forEach(e=>e.addEventListener('input',()=>store(a))));apply();
document.querySelector('#search').oninput=e=>{const q=e.target.value.toLowerCase();articles.forEach(a=>a.hidden=!a.dataset.search.includes(q))};
let queue=[];function stop(){queue=[];for(const a of audios){a.pause();a.currentTime=0}}
function playNext(){if(!queue.length)return;const a=queue.shift();a.currentTime=0;a.play().catch(()=>{queue=[]})}
audios.forEach(a=>a.onended=playNext);document.querySelector('#playAll').onclick=()=>{stop();queue=articles.filter(a=>!a.hidden).map(a=>a.querySelector('audio'));playNext()};document.querySelector('#stop').onclick=stop;
document.querySelector('#export').onclick=()=>{const payload={sampler:key,exportedAt:new Date().toISOString(),clips:clips.map(c=>({...c,review:saved[c.id]||{}}))};const u=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=u;a.download='audio-clips-review.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};
document.querySelector('#import').onclick=()=>document.querySelector('#file').click();document.querySelector('#file').onchange=async e=>{try{const d=JSON.parse(await e.target.files[0].text());for(const c of d.clips||[])if(c.id&&c.review)saved[c.id]=c.review;localStorage.setItem(key,JSON.stringify(saved));apply()}catch(err){alert('Could not read that review JSON.')}};
</script></html>'''.replace("CLIP_DATA", clip_json)
(OUT / "sampler.html").write_text(page, encoding="utf-8")
print(json.dumps({"todayNewUnique": new_count, "todayDuplicatesAlreadyImported": duplicates, "totalUniqueClipsInSampler": len(clips), "sampler": str(OUT / "sampler.html"), "manifest": str(OUT / "manifest.json")}, ensure_ascii=False, indent=2))
