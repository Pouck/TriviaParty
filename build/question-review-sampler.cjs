// Embedded by prepare-question-review-sampler.py; no server or package database required.
const questions = QUESTION_DATA, initial = INITIAL_STATE;
const key = 'question-review-sampler-v2';
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const asText = value => typeof value === 'string' ? value : JSON.stringify(value, null, 2);
const aliases = new Map(questions.flatMap(q => q.legacyIds.map(id => [id, q.id])));
let saved = {};
try { saved = JSON.parse(localStorage.getItem(key) || '{}'); } catch {}
let reviews = {...initial.reviews};
for (const [id, review] of Object.entries(saved.reviews || {})) {
    // Processed baseline changes take effect; preserve edits made after that baseline.
    const canonicalId=aliases.get(id);
    if (!canonicalId) continue;
    const processed=(initial.consumed?.[canonicalId] || []).some(old =>
        String(review.rating ?? '')===old.rating && (review.modification || '')===old.modification);
    if (!processed && (!saved.baseline || JSON.stringify(review) !== JSON.stringify(saved.baseline[id]))) reviews[canonicalId] = review;
}
const history = {...initial.history, ...saved.history};
const selectedPresentation = {};
let visible = [], index = 0;
const notesArea = document.querySelector('#generalNotes');
notesArea.value = saved.generalComments ?? initial.generalComments.join('\n');
function persist() {
    try { localStorage.setItem(key, JSON.stringify({reviews, baseline:initial.reviews, history, generalComments:notesArea.value})); }
    catch { document.querySelector('#saved').textContent = 'Browser storage is full. Export your review now.'; }
}
notesArea.oninput = persist;
const topics = [...new Set(questions.flatMap(q => q.topics))].sort((a,b) => a.localeCompare(b));
for (const topic of topics) {
    const option = document.createElement('option'); option.value = topic; option.textContent = topic;
    document.querySelector('#category').append(option);
}
function reviewed(review) { return review && (review.rating !== '' && review.rating != null || !!review.modification?.trim()); }
function setStatus() {
    document.querySelector('#saved').textContent = `Saved in this browser · ${questions.filter(q => reviewed(reviews[q.id])).length} reviewed / ${questions.length} unique questions`;
    document.querySelector('#counter').textContent = visible.length ? `${index+1} of ${visible.length} shown · ${questions.length} unique questions` : '';
}
function matching() {
    const query = document.querySelector('#search').value.trim().toLowerCase();
    const topic = document.querySelector('#category').value, status = document.querySelector('#status').value;
    const rating = document.querySelector('#ratingFilter').value;
    return questions.filter(q => {
        const review = reviews[q.id] || {};
        if (topic && !q.topics.includes(topic)) return false;
        if (status === 'unreviewed' && reviewed(review) || status === 'reviewed' && !reviewed(review)) return false;
        if (status === 'needs' && String(review.rating) !== '0') return false;
        if (status === 'modified' && !review.modification?.trim()) return false;
        if (rating === 'unrated' && review.rating !== '' && review.rating != null) return false;
        if (rating !== 'all' && rating !== 'unrated' && String(review.rating) !== rating) return false;
        return !query || `${q.id} ${q.legacyIds.join(' ')} ${q.topics.join(' ')} ${q.presentations.map(p => `${p.prompt} ${p.answers.join(' ')} ${p.clues.join(' ')} ${p.label}`).join(' ')}`.toLowerCase().includes(query);
    });
}
function section(title, body) { return body ? `<section class="section"><h3>${esc(title)}</h3>${body}</section>` : ''; }
function list(values) { return values.map(value => `<li>${esc(asText(value))}</li>`).join(''); }
function mapVisual(q) {
    if (!q.mapOptions?.length) return q.image ? `<img class="prompt-image" src="${esc(q.image)}" alt="Question image">` : '';
    const background = q.image ? `<img src="${esc(q.image)}" alt="Carte">` : '<svg viewBox="0 0 1000 600" role="img" aria-label="Carte de démonstration"><rect width="1000" height="600" fill="#254d73"/><path d="M220 80L490 60 680 145 720 290 610 350 590 480 400 540 290 420 320 270 180 190Z" fill="#75a276" stroke="#c5ddbc" stroke-width="6"/></svg>';
    return `<div class="review-map">${background}${q.mapOptions.filter(o => Number.isFinite(o.xRatio) && Number.isFinite(o.yRatio)).map((o,i) => `<span class="map-marker${i===q.correctOptionIndex?' correct':''}" style="left:${Math.max(0,Math.min(1,o.xRatio))*100}%;top:${Math.max(0,Math.min(1,o.yRatio))*100}%">${esc(o.label)}</span>`).join('')}</div>`;
}
function render() {
    visible = matching(); index = Math.min(index, Math.max(visible.length - 1, 0));
    const root = document.querySelector('#main');
    if (!visible.length) { root.innerHTML = '<div class="empty">No questions match these filters.</div>'; setStatus(); return; }
    const entry = visible[index], selection = selectedPresentation[entry.id] || 0;
    const q = {...entry, ...entry.presentations[selection]}, review = reviews[q.id] || {rating:'', modification:''};
    const options = q.options.map((option, i) => `<div class="option ${i === q.correctOptionIndex ? 'correct' : ''}">${esc(asText(option))}${i === q.correctOptionIndex ? ' ✓' : ''}</div>`).join('');
    const variants = entry.presentations.map((p, i) => `<option value="${i}" ${i === selection ? 'selected' : ''}>${esc(p.label)}${p.answerMode === 'WRITTEN' && !/écrit/i.test(p.label) ? ' · written' : ''}${p.answerMode === 'BUZZER' && !/buzzer/i.test(p.label) ? ' · oral' : ''}</option>`).join('');
    const oldReviews = Object.entries(history[q.id] || {}).map(([id, old]) => `<li>${esc(id)}: rating ${esc(old.rating ?? '—')}${old.modification ? ` · ${esc(old.modification)}` : ''}</li>`).join('');
    root.innerHTML = `<article class="card">
        <div class="meta"><span>${esc(q.id)}</span><span>${esc(q.topics.join(' · '))}</span></div>
        <label for="presentation"><b>Play presentation</b></label>
        <select id="presentation" style="display:block;max-width:100%;margin-top:8px">${variants}</select>
        <p class="rating-help">One question · ${entry.presentations.length} presentations. Switching presentation keeps the same question and review.</p>
        <div class="question">${esc(q.prompt)}</div>
        ${q.subQuestion ? `<div class="sub">${esc(asText(q.subQuestion))}</div>` : ''}
        ${mapVisual(q)}
        ${section('Answer choices', options)}
        ${section('Correct answer / accepted answers', q.answers.length ? `<ul>${list(q.answers)}</ul>` : '')}
        ${section('Explanation', esc(q.explanation))}
        ${section(`Progressive clues · ${q.clues.length} indices`, q.clues.length ? `<ol>${list(q.clues)}</ol>` : '')}
        ${section('Items to put in order', q.items.length ? `<ul>${list(q.items)}</ul>` : '')}
        ${section('Correct order', q.correctOrder.length ? `<ol>${list(q.correctOrder)}</ol>` : '')}
        ${oldReviews ? `<details><summary>Preserved reviews from earlier presentations (${Object.keys(history[q.id]).length})</summary><ul>${oldReviews}</ul></details>` : ''}
        <div class="controls"><div><b>Question difficulty</b><div class="rating-options">${['0','1','2','3','4','5'].map(n => `<label><input type="radio" name="rating" value="${n}" ${String(review.rating) === n ? 'checked' : ''}>${n}</label>`).join('')}</div>
        <p class="rating-help">0 = needs review · 1–5 = difficulty. Earlier presentation ratings remain preserved above.</p></div>
        <div><label for="modification"><b>Modification request or correction</b></label><textarea id="modification">${esc(review.modification || '')}</textarea><div class="buttons"><button id="clear">Clear this question review</button><span id="itemSaved" class="status"></span></div></div></div></article>`;
    root.querySelector('#presentation').onchange = event => { selectedPresentation[q.id] = Number(event.target.value); render(); };
    root.querySelectorAll('input[name="rating"]').forEach(input => input.onchange = save);
    root.querySelector('#modification').oninput = save;
    root.querySelector('#clear').onclick = () => { reviews[q.id] = {rating:'', modification:''}; persist(); render(); };
    setStatus();
}
function save() {
    const q = visible[index]; if (!q) return;
    const selected = document.querySelector('input[name="rating"]:checked');
    reviews[q.id] = {rating:selected ? selected.value : '', modification:document.querySelector('#modification').value};
    persist(); setStatus(); document.querySelector('#itemSaved').textContent = 'Saved';
}
function move(delta) {
    if (!visible.length) return;
    index = (index + delta + visible.length) % visible.length; render(); window.scrollTo({top:0, behavior:'smooth'});
}
document.querySelector('#prev').onclick = () => move(-1);
document.querySelector('#next').onclick = () => move(1);
document.querySelector('#nextTodo').onclick = () => {
    for (let offset = 1; offset <= visible.length; offset++) {
        const next = (index + offset) % visible.length;
        if (!reviewed(reviews[visible[next].id])) { index = next; render(); return; }
    }
    alert('All questions in this view have a review.');
};
for (const id of ['search','category','status','ratingFilter']) document.querySelector('#'+id).addEventListener(id === 'search' ? 'input' : 'change', () => { index = 0; render(); });
document.querySelector('#export').onclick = () => {
    const payload = {sampler:'question-review-sampler-v2', exportedAt:new Date().toISOString(),
        ratingMeaning:{0:'Needs review',1:'Very easy',2:'Easy',3:'Moderate',4:'Difficult',5:'Very difficult'},
        generalComments:notesArea.value.split('\n').map(x => x.trim()).filter(Boolean),
        reviews:questions.filter(q => reviews[q.id] || history[q.id]).map(q => ({questionId:q.id, legacyIds:q.legacyIds,
            topics:q.topics, prompt:q.prompt, rating:reviews[q.id]?.rating === '' || reviews[q.id]?.rating == null ? null : Number(reviews[q.id].rating),
            modification:reviews[q.id]?.modification || '', presentationReviews:Object.values(history[q.id] || {})}))};
    const link = document.createElement('a'); link.href = URL.createObjectURL(new Blob([JSON.stringify(payload,null,2)], {type:'application/json'}));
    link.download = 'question-review-feedback.json'; link.click(); setTimeout(() => URL.revokeObjectURL(link.href), 1000);
};
document.querySelector('#import').onclick = () => document.querySelector('#file').click();
document.querySelector('#file').onchange = async event => {
    try {
        const data = JSON.parse(await event.target.files[0].text());
        const grouped = new Map();
        for (const row of data.reviews || []) {
            const id = aliases.get(row.questionId); if (!id) continue;
            const rows = grouped.get(id) || []; rows.push(row); grouped.set(id, rows);
            if (data.sampler !== 'question-review-sampler-v2') (history[id] ||= {})[row.questionId] = row;
            for (const previous of row.presentationReviews || []) (history[id] ||= {})[previous.questionId] = previous;
        }
        for (const [id, rows] of grouped) {
            const ratings = [...new Set(rows.map(r => r.rating).filter(r => r != null))];
            reviews[id] = {rating:ratings.length === 1 ? String(ratings[0]) : '', modification:[...new Set(rows.map(r => r.modification).filter(Boolean))].join('\n')};
        }
        if (Array.isArray(data.generalComments)) notesArea.value = data.generalComments.join('\n');
        persist(); render();
    } catch { alert('Could not read that review file.'); }
};
render();
