const fs = require('fs');

const filePath = 'H:/AndroidStudioProjects/TriviaParty/leaf_subjects_inventory.artifact.md';
let content = fs.readFileSync(filePath, 'utf8');

const lines = content.split('\n');

// Let's refine the cleaning logic:
// Rules:
// 1. Remove over-specified labels, raw answers, non-label phrases, dates/numbers (already pruned via 'not a suitable leaf').
// 2. Keep labels short, categorical, and strictly in French.
// 3. Remove articles ("Le", "La", "Un", "Une", "L’", "Les") unless part of a specific title (painting, book, building/site, monument, or proper noun where article is an inseparable part of the name like Le Havre, Le Caire, La Havane, etc.).
// 4. Strip gender where applicable.
// 5. Normalize Person Names: Ensure all person/artist names follow a consistent format (e.g. standard Full Name).

function cleanLabel(label, type) {
    let clean = label.trim();

    // If person, ensure standard full name capitalization
    if (type === 'person') {
        return clean;
    }

    // For general terms, remove leading articles if not a proper name / title / building / city / country
    // Articles to strip: Le, La, L’, Les, Un, Une (case insensitive)
    // But preserve if type is building-or-site, city, country, landscape, museum, or specific titles
    const preserveTypes = ['building-or-site', 'city', 'country', 'landscape', 'museum', 'architectural-style'];
    if (!preserveTypes.includes(type)) {
        // Strip leading articles
        clean = clean.replace(/^(le|la|l’|l'|les|un|une)\s+/i, '');
    }

    return clean;
}

let outputLines = [];
// Keep intro comments
let introDone = false;
let currentHeader = '';
let rows = [];

for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    if (line.startsWith('# Inventaire') || line.startsWith('General comments:') || line.startsWith('- ') || line.trim() === '' && !introDone) {
        outputLines.push(line);
        if (line.startsWith('Ce document')) {
            introDone = true;
        }
        continue;
    }

    if (line.startsWith('## ')) {
        if (rows.length > 0) {
            // Output previous section with updated count
            outputLines.push(currentHeader.replace(/\(\d+ sujets\)/, `(${rows.length} sujets)`));
            outputLines.push('');
            outputLines.push('| ID | Label | Type | Statut | Aliases / Notes | Review / Comments |');
            outputLines.push('|---|---|---|---|---|---|');
            for (let r of rows) {
                outputLines.push(`| ${r.id} | **${r.label}** | ${r.type} | ${r.statut} | ${r.aliases} | ${r.review} |`);
            }
            outputLines.push('');
            rows = [];
        }
        currentHeader = line;
    } else if (line.startsWith('| ID |') || line.startsWith('|---|')) {
        // skip table header/separator as we regenerate them
        continue;
    } else if (line.startsWith('|')) {
        let parts = line.split('|').map(p => p.trim());
        let id = parts[1];
        let rawLabel = parts[2].replace(/\*\*/g, '').trim();
        let type = parts[3];
        let statut = parts[4];
        let aliases = parts[5];
        let review = parts[6] || '';

        if (review.toLowerCase().includes('not a suitable leaf')) {
            continue; // Pruned
        }

        let label = cleanLabel(rawLabel, type);
        rows.push({ id, label, type, statut, aliases, review });
    }
}

// Push last section
if (rows.length > 0 && currentHeader) {
    outputLines.push(currentHeader.replace(/\(\d+ sujets\)/, `(${rows.length} sujets)`));
    outputLines.push('');
    outputLines.push('| ID | Label | Type | Statut | Aliases / Notes | Review / Comments |');
    outputLines.push('|---|---|---|---|---|---|');
    for (let r of rows) {
        outputLines.push(`| ${r.id} | **${r.label}** | ${r.type} | ${r.statut} | ${r.aliases} | ${r.review} |`);
    }
    outputLines.push('');
}

fs.writeFileSync(filePath, outputLines.join('\n'), 'utf8');
console.log("Successfully processed and updated leaf_subjects_inventory.artifact.md!");
