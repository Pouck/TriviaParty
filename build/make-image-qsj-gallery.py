from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / "game-library" / "bank"
OUT = ROOT / "build" / "image-qsj-gallery"
MEDIA = BANK / "media"
OUT_MEDIA = OUT / "media"
REVIEW_IMPORT = OUT / "review-imported-2026-10-28-latest.json"

bank = json.loads((BANK / "questions.json").read_text(encoding="utf-8"))
images: dict[str, dict] = {}
missing = []

for question in bank.get("questions", []):
    for presentation in question.get("presentations", []):
        content = presentation.get("content", {})
        image_url = content.get("imageUrl", "")
        if not content.get("imageRevealMode") or not image_url.startswith("media/"):
            continue
        filename = image_url.split("/", 1)[1]
        source = MEDIA / filename
        if not source.is_file():
            missing.append((question.get("id"), image_url))
            continue

        category_path = presentation.get("legacyCategory", "")
        parts = category_path.split(" — ")
        category = parts[-2] if len(parts) > 1 else presentation.get("topic", "Autres")
        if "Personnages de bande dessinée" in category_path or "Personnages de BD" in category_path:
            category = "Personnages de BD"

        image = images.setdefault(filename, {
            "id": "gallery-" + filename.rsplit(".", 1)[0],
            "answers": [],
            "categories": [],
            "categoryPaths": [],
            "image": "media/" + filename,
            "questions": [],
            "facts": [],
        })
        for answer in question.get("answers", []):
            if answer not in image["answers"]:
                image["answers"].append(answer)
        for value, target in ((category, "categories"), (category_path, "categoryPaths")):
            if value and value not in image[target]:
                image[target].append(value)
        presentation_id = presentation.get("id", question["id"])
        if presentation_id not in image["questions"]:
            image["questions"].append(presentation_id)
        facts = question.get("imageFacts")
        if facts and not any(row.get("subjectTitle") == facts.get("subjectTitle") for row in image["facts"]):
            image["facts"].append(facts)

OUT.mkdir(parents=True, exist_ok=True)
OUT_MEDIA.mkdir(parents=True, exist_ok=True)
for filename in images:
    shutil.copyfile(MEDIA / filename, OUT_MEDIA / filename)

items = sorted(images.values(), key=lambda x: (x["categories"][0].casefold(), x["answers"][0].casefold(), x["id"]))
data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
review_items = {}
if REVIEW_IMPORT.is_file():
    review_doc = json.loads(REVIEW_IMPORT.read_text(encoding="utf-8"))
    review_items = review_doc.get("items", {})
review_json = json.dumps(review_items, ensure_ascii=False).replace("</", "<\\/")
page = r'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Qui suis-je? image gallery</title>
<style>
:root{color-scheme:light;font:16px system-ui,sans-serif;background:#eef1f5;color:#182432}*{box-sizing:border-box}body{margin:0 auto;padding:16px;max-width:1800px}.head{position:sticky;top:0;z-index:3;background:#eef1f5f2;backdrop-filter:blur(10px);padding:8px 0 14px}.head h1{margin:2px 0 5px}.head p{margin:4px 0 12px;color:#465668;max-width:1000px;line-height:1.45}.toolbar{display:flex;gap:9px;align-items:center;flex-wrap:wrap}.toolbar select,.toolbar input,.toolbar button,.card button,.export{font:inherit;border:1px solid #aab7c5;border-radius:9px;padding:9px 11px;background:white;color:inherit}.toolbar select{min-width:205px}.toolbar input{flex:1;min-width:240px}.toolbar button,.card button{cursor:pointer}.toolbar button:hover,.card button:hover{background:#e3edf8}.count{font-weight:650;margin-left:auto}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,340px),1fr));gap:16px;align-items:start}.card{background:white;border:1px solid #cbd3dc;border-radius:13px;overflow:hidden;box-shadow:0 2px 7px #17263812}.thumb{height:340px;display:grid;place-items:center;background-color:#fff;background-image:linear-gradient(45deg,#eef1f5 25%,transparent 25%),linear-gradient(-45deg,#eef1f5 25%,transparent 25%),linear-gradient(45deg,transparent 75%,#eef1f5 75%),linear-gradient(-45deg,transparent 75%,#eef1f5 75%);background-size:20px 20px;background-position:0 0,0 10px,10px -10px,-10px 0}.thumb img{width:100%;height:100%;object-fit:contain;cursor:zoom-in}.info{padding:12px 13px 14px}.category{color:#445b70;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.035em}.answer{font-size:20px;font-weight:750;margin:4px 0 5px}.facts{font-size:14px;color:#48596a;line-height:1.4;margin:4px 0 9px}.rating{display:flex;gap:7px;flex-wrap:wrap}.rating button{font-size:13px;padding:7px 9px}.rating button.active[data-rating="good"]{background:#d9f2e2;border-color:#5a9c72}.rating button.active[data-rating="review"]{background:#fff0c7;border-color:#c49d31}.rating button.active[data-rating="replace"]{background:#ffe0dc;border-color:#c56e64}.note{width:100%;margin-top:8px;min-height:44px;resize:vertical;border:1px solid #c1cad4;border-radius:8px;padding:8px;font:14px system-ui,sans-serif}.cardFoot{font-size:12px;color:#687889;margin-top:6px}.empty{padding:30px;color:#4a5c6e}.modal{position:fixed;inset:0;z-index:10;background:#111d;display:none;place-items:center;padding:20px}.modal.open{display:grid}.modal img{max-width:96vw;max-height:91vh;object-fit:contain;background:white;border-radius:8px}.modal button{position:fixed;right:18px;top:14px;background:#fff;border:0;border-radius:50%;font-size:24px;width:44px;height:44px;cursor:pointer}.hidden{display:none!important}@media(max-width:650px){.head{position:static}.thumb{height:300px}.count{margin-left:0;width:100%}.grid{grid-template-columns:1fr}}
</style>
<header class="head">
<h1>Qui suis-je ? — image gallery</h1>
<p>Browse the complete picture set at full size to judge image quality and variety. Use the approval filter to find images that are unrated, marked for review, or marked for replacement. Your review is saved in this browser; export it to keep a copy.</p>
<div class="toolbar"><select id="approval" aria-label="Approval status"><option value="">All approval statuses</option><option value="pending">Needs approval</option><option value="replace">Needs replacement</option><option value="approved">Approved</option></select><select id="category"><option value="">All categories</option></select><input id="search" placeholder="Search answer or category…"><button id="clear">Clear filters</button><button id="export">Export review</button><span class="count" id="count"></span></div>
</header>
<main class="grid" id="grid"></main>
<div class="modal" id="modal"><button id="close" aria-label="Close">×</button><img id="large" alt=""></div>
<script>
const ITEMS=__GALLERY_ITEMS_JSON__,SEED=__GALLERY_REVIEW_JSON__,STORE='qsj-image-gallery-review-v1';
const $=id=>document.getElementById(id);let state={};
try{state={...JSON.parse(localStorage.getItem(STORE)||'{}'),...SEED}}catch{state=SEED}
const cats=[...new Set(ITEMS.flatMap(x=>x.categories))].sort((a,b)=>a.localeCompare(b));
for(const c of cats){const o=document.createElement('option');o.value=c;o.textContent=c;$('category').append(o)}
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function save(){localStorage.setItem(STORE,JSON.stringify(state))}
function render(){const cat=$('category').value,approval=$('approval').value,needle=$('search').value.trim().toLocaleLowerCase();const base=ITEMS.filter(x=>(!cat||x.categories.includes(cat))&&(!needle||(x.answers.join(' ')+' '+x.categories.join(' ')+' '+x.categoryPaths.join(' ')).toLocaleLowerCase().includes(needle)));const needsApproval=base.filter(x=>!['good','replace'].includes((state[x.id]||{}).rating)).length;const needsReplacement=base.filter(x=>(state[x.id]||{}).rating==='replace').length;const filtered=base.filter(x=>!approval||(approval==='pending'?(!['good','replace'].includes((state[x.id]||{}).rating)):approval==='replace'?((state[x.id]||{}).rating==='replace'):((state[x.id]||{}).rating==='good')));$('count').textContent=filtered.length+' of '+base.length+' matching images · '+needsApproval+' need approval · '+needsReplacement+' need replacement';$('grid').replaceChildren();if(!filtered.length){$('grid').innerHTML='<div class="empty">No images match these filters.</div>';return}for(const item of filtered){const saved=state[item.id]||{};const art=document.createElement('article');art.className='card';const title=item.answers[0]||'Untitled';const category=item.categories.join(' · ');const french=[...new Set((item.facts||[]).map(f=>f.frenchTitle).filter(Boolean))];const facts=[...french.map(x=>'Nom français : '+x),...new Set((item.facts||[]).flatMap(f=>(f.facts||[]).filter(x=>x.kind!=='media_creator').map(x=>(x.role||x.kind)+': '+x.value)))].slice(0,3);art.innerHTML=`<div class="thumb"><img loading="lazy" src="${esc(item.image)}" alt="${esc(title)}"></div><div class="info"><div class="category">${esc(category)}</div><div class="answer">${esc(title)}</div>${facts.length?`<div class="facts">${facts.map(esc).join('<br>')}</div>`:''}<div class="rating">${[['good','Looks good'],['review','Review'],['replace','Replace']].map(([v,l])=>`<button data-rating="${v}" class="${saved.rating===v?'active':''}">${l}</button>`).join('')}</div><textarea class="note" placeholder="Optional note…">${esc(saved.note||'')}</textarea><div class="cardFoot">${item.questions.length>1?item.questions.length+' linked presentations':'1 presentation'}</div></div>`;const img=art.querySelector('img');img.onclick=()=>openModal(item.image,title);for(const b of art.querySelectorAll('[data-rating]'))b.onclick=()=>{const old=state[item.id]||{};state[item.id]={...old,rating:b.dataset.rating};save();render()};const note=art.querySelector('.note');note.onchange=()=>{state[item.id]={...(state[item.id]||{}),note:note.value};save()};$('grid').append(art)}}
function openModal(src,alt){$('large').src=src;$('large').alt=alt;$('modal').classList.add('open')}function closeModal(){$('modal').classList.remove('open');$('large').src=''}
$('approval').onchange=()=>{if(['pending','replace'].includes($('approval').value)){$('category').value='';$('search').value=''}render()};$('category').onchange=render;$('search').oninput=render;$('clear').onclick=()=>{$('approval').value='';$('category').value='';$('search').value='';render()};$('close').onclick=closeModal;$('modal').onclick=e=>{if(e.target===$('modal'))closeModal()};document.onkeydown=e=>{if(e.key==='Escape')closeModal()};$('export').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({schema:'qsj-image-gallery-review-v1',exportedAt:new Date().toISOString(),items:state},null,2)],{type:'application/json'}));a.download='qsj-image-gallery-review.json';a.click();URL.revokeObjectURL(a.href)};render();
</script></html>'''.replace("__GALLERY_ITEMS_JSON__", data).replace("__GALLERY_REVIEW_JSON__", review_json)
(OUT / "index.html").write_text(page, encoding="utf-8")
(OUT / "README.txt").write_text(
    "Open index.html in a browser to review large thumbnails of each unique picture. Filter approval, replacement, or category; search; zoom; and save review ratings/notes in browser storage. Needs approval includes unrated and Review images. Needs replacement shows Replace ratings. Export a JSON copy before changing browser or device. This catalog is separate from the timed reveal sampler.\n",
    encoding="utf-8",
)
print(json.dumps({"uniqueImages": len(images), "categories": len({c for x in items for c in x["categories"]}), "missing": missing, "sampler": str(OUT / "index.html")}, ensure_ascii=False, indent=2))
