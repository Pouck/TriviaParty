from __future__ import annotations

import html
import json
import zipfile
from pathlib import Path, PurePosixPath
from datetime import datetime

ROOT = Path.cwd()
LIBRARY = ROOT / "game-library" / "current"
OUT = ROOT / "build" / "question-review-sampler"
ASSETS = OUT / "assets"
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def text(value):
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)


def collect():
    questions = []
    images_copied = 0
    missing_images = []
    for archive_path in sorted(LIBRARY.glob("*.zip"), key=lambda p: p.name.casefold()):
        package_id = archive_path.stem
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
            game = {}
            if "game.json" in names:
                try:
                    game = json.loads(archive.read("game.json").decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    pass
            bank_names = sorted(n for n in names if n.startswith("question-bank/") and n.endswith(".json"))
            for bank_name in bank_names:
                bank = json.loads(archive.read(bank_name).decode("utf-8"))
                bank_questions = bank if isinstance(bank, list) else bank.get("questions", [])
                for q in bank_questions:
                    qid = q.get("id")
                    if not qid:
                        continue
                    image_ref = q.get("imageUrl")
                    local_image = ""
                    if image_ref:
                        candidate = PurePosixPath(str(image_ref).replace("\\", "/"))
                        if candidate.is_absolute() or ".." in candidate.parts:
                            missing_images.append({"questionId": qid, "imageUrl": image_ref})
                        elif candidate.as_posix() in names:
                            relative = Path("assets") / package_id / Path(*candidate.parts)
                            target = OUT / relative
                            target.parent.mkdir(parents=True, exist_ok=True)
                            if not target.exists():
                                target.write_bytes(archive.read(candidate.as_posix()))
                                images_copied += 1
                            local_image = relative.as_posix()
                        else:
                            missing_images.append({"questionId": qid, "imageUrl": image_ref})

                    options = q.get("options") or []
                    answer = q.get("acceptableAnswers") or []
                    correct_index = q.get("correctOptionIndex")
                    if isinstance(correct_index, int) and 0 <= correct_index < len(options):
                        answer = [options[correct_index]]
                    items = q.get("items") or []
                    by_id = {str(item.get("id")): item for item in items if isinstance(item, dict) and item.get("id") is not None}
                    order_ids = q.get("correctOrderIds") or []
                    ordered = [by_id[str(item_id)] for item_id in order_ids if str(item_id) in by_id]
                    questions.append({
                        "id": qid,
                        "packageId": package_id,
                        "packageName": game.get("name", package_id),
                        "category": q.get("category", bank.get("category", "")),
                        "subject": game.get("subject", bank.get("subject", "")),
                        "kind": q.get("kind", ""),
                        "answerMode": bank.get("answerMode", ""),
                        "prompt": q.get("prompt", ""),
                        "subQuestion": q.get("subQuestion", ""),
                        "options": options,
                        "correctOptionIndex": correct_index,
                        "answers": answer,
                        "clues": q.get("clues") or [],
                        "items": items,
                        "correctOrder": ordered,
                        "randomVariants": q.get("randomVariants") or [],
                        "image": local_image,
                        "imageSource": image_ref or "",
                    })
    return questions, images_copied, missing_images


OUT.mkdir(parents=True, exist_ok=True)
questions, images_copied, missing_images = collect()
assert questions, "No questions found in playable library archives"
if len({q["id"] for q in questions}) != len(questions):
    raise SystemExit("Question IDs are not unique; refusing to create an ambiguous review sampler.")

manifest = {
    "createdAt": datetime.now().astimezone().isoformat(),
    "questionCount": len(questions),
    "packageCount": len({q["packageId"] for q in questions}),
    "imagesCopied": images_copied,
    "missingImages": missing_images,
    "ratingScale": {"0": "Needs review", "1-5": "Difficulty"},
    "questions": questions,
}
(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

data = json.dumps(questions, ensure_ascii=False).replace("</", "<\\/")
state_path = OUT / "review-state.json"
review_state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {"reviews": [], "generalComments": []}
initial_reviews = {
    row["questionId"]: {
        "rating": "" if row.get("rating") is None else str(row.get("rating")),
        "modification": row.get("modification", "") or "",
    }
    for row in review_state.get("reviews", []) if row.get("questionId")
}
initial = json.dumps({
    "reviews": initial_reviews,
    "generalComments": review_state.get("generalComments", []),
}, ensure_ascii=False).replace("</", "<\\/")
page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Question review sampler</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101725;color:#eef3ff;font:17px system-ui,sans-serif;max-width:1150px;padding:20px;margin-inline:auto}button,input,select,textarea{font:inherit;color:inherit;background:#202f44;border:1px solid #526780;border-radius:9px;padding:10px}button{cursor:pointer}.top{position:sticky;top:0;background:#101725ee;backdrop-filter:blur(10px);z-index:3;padding:10px 0}.filters,.nav{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}.filters input{flex:1;min-width:230px}.counter{margin-left:auto;color:#c6d6eb}.card{background:#1b293c;border:1px solid #405674;border-radius:16px;padding:clamp(16px,3vw,30px);margin-top:18px}.meta{color:#b9c9dc;font-size:14px}.meta span{display:inline-block;margin:0 10px 8px 0}.question{font-size:clamp(22px,3.2vw,34px);line-height:1.3;margin:18px 0;font-weight:700;white-space:pre-wrap}.sub{font-size:20px;color:#d4e1f3;white-space:pre-wrap}.prompt-image{display:block;max-width:min(100%,650px);max-height:420px;object-fit:contain;background:#0e1723;border-radius:10px;margin:18px auto}.section{background:#24354a;border-radius:11px;padding:14px 18px;margin:12px 0}.section h3{font-size:15px;text-transform:uppercase;letter-spacing:.06em;color:#9fcfff;margin:0 0 8px}.section p,.section li{line-height:1.5;white-space:pre-wrap}.option{padding:9px 12px;border-radius:8px;background:#1a2637;margin:6px 0}.correct{border:2px solid #65d99b;background:#16382e}.controls{border-top:1px solid #405674;margin-top:22px;padding-top:20px;display:grid;grid-template-columns:minmax(250px,1fr) minmax(300px,2fr);gap:18px}.rating-options{display:flex;gap:8px;flex-wrap:wrap}.rating-options label{display:flex;align-items:center;gap:5px;background:#24354a;padding:10px 13px;border-radius:9px;cursor:pointer}.rating-options input{accent-color:#65d99b}.rating-help{color:#b9c9dc;font-size:13px;margin-top:8px}.controls textarea{width:100%;min-height:125px;resize:vertical}.buttons{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}.status{color:#8fe5b0;align-self:center}.empty{padding:40px;text-align:center;color:#c3d2e4}
</style><div class="top"><h1>Question review sampler</h1><div class="filters"><input id="search" type="search" placeholder="Search category, question, answer, package…"><select id="category"><option value="">All categories</option></select><select id="status"><option value="all">All questions</option><option value="unreviewed">Not reviewed</option><option value="reviewed">Reviewed</option><option value="needs">Rated 0 · Needs review</option><option value="modified">Has modification note</option></select><select id="ratingFilter"><option value="all">Any rating</option><option value="unrated">Unrated</option><option value="0">Rating 0 · Needs review</option><option value="1">Rating 1 · Very easy</option><option value="2">Rating 2 · Easy</option><option value="3">Rating 3 · Moderate</option><option value="4">Rating 4 · Difficult</option><option value="5">Rating 5 · Very difficult</option></select><span class="counter" id="counter"></span></div><details class="general"><summary>General review notes</summary><p>These reminders stay with the exported feedback. Edit them if needed.</p><textarea id="generalNotes"></textarea></details><div class="nav"><button id="prev">← Previous</button><button id="next">Next →</button><button id="nextTodo">Next unreviewed</button><button id="export">Export review</button><button id="import">Load review JSON</button><input id="file" type="file" accept="application/json" hidden><span class="status" id="saved"></span></div></div><main id="main"></main>
<script>
const questions=QUESTION_DATA, initial=INITIAL_STATE, key='question-review-sampler-v1';let localReviews={};try{localReviews=JSON.parse(localStorage.getItem(key)||'{}')}catch{}let reviews={...localReviews,...initial.reviews};let visible=[],index=0;const generalKey=key+'-general';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const asText=v=>typeof v==='string'?v:JSON.stringify(v,null,2);
const categories=[...new Set(questions.map(q=>q.category).filter(Boolean))].sort((a,b)=>a.localeCompare(b));for(const c of categories){const o=document.createElement('option');o.value=c;o.textContent=c;document.querySelector('#category').append(o)}
function reviewCount(){return Object.values(reviews).filter(r=>r&&(r.rating!==''||r.modification?.trim())).length}
function setStatus(){document.querySelector('#saved').textContent=`Saved in this browser · ${reviewCount()} reviewed / ${questions.length}`;document.querySelector('#counter').textContent=visible.length?`${index+1} of ${visible.length} shown · ${questions.length} total`:''}
function matching(){const query=document.querySelector('#search').value.trim().toLowerCase(),category=document.querySelector('#category').value,status=document.querySelector('#status').value,ratingFilter=document.querySelector('#ratingFilter').value;return questions.filter(q=>{if(category&&q.category!==category)return false;const r=reviews[q.id]||{},done=r.rating!==''&&r.rating!==undefined||!!r.modification?.trim();if(status==='unreviewed'&&done)return false;if(status==='reviewed'&&!done)return false;if(status==='needs'&&String(r.rating)!=='0')return false;if(status==='modified'&&!r.modification?.trim())return false;if(ratingFilter==='unrated'&&r.rating!==''&&r.rating!==undefined)return false;if(ratingFilter!=='all'&&ratingFilter!=='unrated'&&String(r.rating)!==ratingFilter)return false;if(query&&!`${q.category} ${q.prompt} ${q.packageName} ${q.packageId} ${q.answers.join(' ')} ${q.options.join(' ')}`.toLowerCase().includes(query))return false;return true})}
function section(title,body){return body?`<section class="section"><h3>${title}</h3>${body}</section>`:''}
function render(){visible=matching();if(index>=visible.length)index=Math.max(0,visible.length-1);const root=document.querySelector('#main');if(!visible.length){root.innerHTML='<div class="empty">No questions match these filters.</div>';setStatus();return}const q=visible[index],r=reviews[q.id]||{rating:'',modification:''};
let opts=q.options.map((o,i)=>`<div class="option ${i===q.correctOptionIndex?'correct':''}">${String.fromCharCode(65+i)}. ${esc(asText(o))}${i===q.correctOptionIndex?' ✓':''}</div>`).join('');
let clues=q.clues.map((c,i)=>`<li><b>${i+1}.</b> ${esc(asText(c))}</li>`).join('');let items=q.items.map(i=>`<li>${esc(asText(i))}</li>`).join('');let order=q.correctOrder.map((i,n)=>`<li><b>${n+1}.</b> ${esc(asText(i))}</li>`).join('');let answers=q.answers.map(a=>`<li>${esc(asText(a))}</li>`).join('');
const chronological=q.category.toLowerCase().includes('chronologie');
root.innerHTML=`<article class="card"><div class="meta"><span>${esc(q.id)}</span><span>${esc(q.packageName)} · ${esc(q.packageId)}</span><span>${esc(q.category)}</span><span>${esc(q.kind)} · ${esc(q.answerMode)}</span></div><div class="question">${esc(q.prompt)}</div>${q.subQuestion?`<div class="sub">${esc(q.subQuestion)}</div>`:''}${q.image?`<img class="prompt-image" loading="lazy" src="${esc(q.image)}" alt="Question image">`:''}${opts?section('Answer choices',opts):''}${answers?section('Correct answer / accepted answers',`<ul>${answers}</ul>`):''}${clues?section('All clues',`<ol>${clues}</ol>`):''}${items?section('Items to put in order',`<ul>${items}</ul>`):''}${order?section(chronological?'Correct chronological order · oldest to newest':'Correct order',`<ol>${order}</ol>`):''}${q.randomVariants.length?section('Question variants',`<pre>${esc(JSON.stringify(q.randomVariants,null,2))}</pre>`):''}<div class="controls"><div><b>Confirm difficulty rating</b><div class="rating-options">${['0','1','2','3','4','5'].map(n=>`<label><input type="radio" name="rating" value="${n}" ${String(r.rating)===n?'checked':''}>${n}</label>`).join('')}</div><div class="rating-help">0 = needs review · 1–5 = difficulty · leave blank = not reviewed</div></div><div><label for="modification"><b>Modification request or correction</b></label><textarea id="modification" placeholder="Describe the exact change you want…">${esc(r.modification||'')}</textarea><div class="buttons"><button id="clear">Clear this review</button><span class="status" id="itemSaved"></span></div></div></div></article>`;
root.querySelectorAll('input[name="rating"]').forEach(e=>e.onchange=()=>save());root.querySelector('#modification').oninput=()=>save();root.querySelector('#clear').onclick=()=>{delete reviews[q.id];persist();render()};setStatus();
}
function save(){const q=visible[index];if(!q)return;const selected=document.querySelector('input[name="rating"]:checked');reviews[q.id]={rating:selected?selected.value:'',modification:document.querySelector('#modification').value};if(!reviews[q.id].modification&&!reviews[q.id].rating)delete reviews[q.id];persist();setStatus();document.querySelector('#itemSaved').textContent='Saved';}
function persist(){try{localStorage.setItem(key,JSON.stringify(reviews))}catch{document.querySelector('#saved').textContent='Browser storage full; export your review JSON now.'}}
function move(delta){if(!visible.length)return;index=(index+delta+visible.length)%visible.length;render();window.scrollTo({top:0,behavior:'smooth'})}
document.querySelector('#prev').onclick=()=>move(-1);document.querySelector('#next').onclick=()=>move(1);document.querySelector('#nextTodo').onclick=()=>{if(!visible.length)return;for(let n=1;n<=visible.length;n++){const i=(index+n)%visible.length,q=visible[i],r=reviews[q.id]||{};if(!(r.rating!==''&&r.rating!==undefined||r.modification?.trim())){index=i;render();window.scrollTo({top:0,behavior:'smooth'});return}}alert('All questions in this view have a rating or modification note.')};
for(const id of ['search','category','status'])document.querySelector('#'+id).addEventListener(id==='search'?'input':'change',()=>{index=0;render()});
const notesArea=document.querySelector('#generalNotes');notesArea.value=localStorage.getItem(generalKey)||initial.generalComments.join('\\n');notesArea.oninput=()=>localStorage.setItem(generalKey,notesArea.value);
document.querySelector('#export').onclick=()=>{const payload={sampler:'question-review-sampler-v1',exportedAt:new Date().toISOString(),ratingMeaning:{0:'Needs review',1:'Very easy',2:'Easy',3:'Moderate',4:'Difficult',5:'Very difficult'},generalComments:notesArea.value.split('\\n').map(x=>x.trim()).filter(Boolean),reviews:questions.filter(q=>reviews[q.id]).map(q=>({questionId:q.id,category:q.category,packageId:q.packageId,prompt:q.prompt,rating:reviews[q.id].rating===''?null:Number(reviews[q.id].rating),modification:reviews[q.id].modification||''}))};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}));a.download='question-review-feedback.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
document.querySelector('#import').onclick=()=>document.querySelector('#file').click();document.querySelector('#file').onchange=async e=>{try{const d=JSON.parse(await e.target.files[0].text());for(const r of d.reviews||[])if(r.questionId)reviews[r.questionId]={rating:r.rating==null?'':String(r.rating),modification:r.modification||''};if(Array.isArray(d.generalComments))notesArea.value=d.generalComments.join('\\n');persist();localStorage.setItem(generalKey,notesArea.value);render()}catch{alert('Could not read that review file.')}};
document.querySelector('#ratingFilter').addEventListener('change',()=>{index=0;render()});
render();
</script></html>'''.replace("QUESTION_DATA", data).replace("INITIAL_STATE", initial)
(OUT / "sampler.html").write_text(page, encoding="utf-8")

print(json.dumps({
    "questions": len(questions),
    "packages": len({q["packageId"] for q in questions}),
    "questionsWithImages": sum(bool(q["image"]) for q in questions),
    "imagesCopied": images_copied,
    "missingImages": len(missing_images),
    "sampler": str(OUT / "sampler.html"),
    "manifest": str(OUT / "manifest.json"),
}, ensure_ascii=False, indent=2))
