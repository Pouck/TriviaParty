"""Add French display names and accepted aliases to image-backed art/site entries."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BANK = ROOT / 'game-library/bank/questions.json'

# French gallery/game names paired with the artwork's original title. These are
# conventional French catalogue names, with a literal French rendering where no
# firmly established title is in ordinary use.
NAMES = {
    'image-qsj-painting-003': "L'École d'Athènes",
    'image-qsj-painting-008': "La Création d'Adam",
    'image-qsj-painting-009': 'Les Tournesols',
    'image-qsj-painting-010': 'Saturne dévorant un de ses fils',
    'image-qsj-painting-013': 'Le Jardin des délices',
    'image-qsj-painting-016': 'Ivan le Terrible et son fils Ivan le 16 novembre 1581',
    'image-qsj-painting-018': 'Les Nymphéas',
    'image-qsj-painting-022': 'Le Jugement dernier',
    'image-qsj-painting-023': 'Madame X',
    'image-qsj-painting-028': 'Les Époux Arnolfini',
    'image-qsj-painting-029': 'Les Ambassadeurs',
    'image-qsj-painting-031': 'La Vierge aux rochers',
    'image-qsj-painting-032': "Un dimanche après-midi à l'île de la Grande Jatte",
    'image-qsj-painting-034': 'Le Printemps',
    'image-qsj-painting-035': 'Les Iris',
    'image-qsj-painting-036': 'Le Serment des Horaces',
    'image-qsj-painting-037': 'La Mort de Socrate',
    'image-qsj-painting-038': "La Dame à l'hermine",
    'image-qsj-painting-040': 'Le 3 mai 1808',
    'image-qsj-painting-041': "L'Escarpolette",
    'image-qsj-painting-043': 'Washington traversant le Delaware',
    'image-qsj-painting-045': 'La Vierge, l’Enfant Jésus et sainte Anne',
    'image-qsj-painting-046': 'Le Garçon bleu',
    'image-qsj-painting-047': 'La Tour de Babel',
    'image-qsj-painting-048': "Le Déjeuner sur l'herbe",
    'image-qsj-painting-052': 'La Mort de Marat',
    'image-qsj-painting-053': 'La Mère de Whistler',
    'image-qsj-painting-054': 'Salvator Mundi',
    'image-qsj-painting-057': 'Le Sacre de Napoléon',
    'image-qsj-painting-058': 'Le Cauchemar',
    'image-qsj-painting-060': 'La Transfiguration',
    'image-qsj-painting-062': 'Portrait d’Adèle Bloch-Bauer I',
    'image-qsj-painting-063': 'Saint Jean-Baptiste',
    'image-qsj-painting-069': 'Napoléon franchissant le Grand-Saint-Bernard',
    'image-qsj-painting-070': "La Vénus d'Urbin",
    'image-qsj-painting-073': 'Les Mangeurs de pommes de terre',
    'image-qsj-painting-074': 'La Dame de Shalott',
    'image-qsj-painting-077': "L'Agneau mystique",
    'image-qsj-painting-078': 'Le Chardonneret',
    'image-qsj-painting-079': 'Les Joueurs de cartes',
    'image-qsj-painting-081': 'L’Angélus',
    'image-qsj-painting-082': 'Nuit étoilée sur le Rhône',
    'image-qsj-painting-083': 'Champ de blé aux corbeaux',
    'image-qsj-painting-084': 'La Laitière',
    'image-qsj-painting-085': 'Autoportrait (1889)',
    'image-qsj-painting-087': 'La Charrette de foin',
    'image-qsj-painting-088': 'Terrasse de café le soir',
    'image-qsj-painting-089': 'L’Annonciation',
    'image-qsj-painting-092': 'Le Retour du fils prodigue',
    'image-qsj-painting-093': 'Le Téméraire remorqué à son dernier mouillage',
    'image-qsj-painting-095': 'La Grande Odalisque',
    'image-qsj-painting-096': 'La Vocation de saint Matthieu',
    'image-qsj-painting-097': 'D’où venons-nous ? Que sommes-nous ? Où allons-nous ?',
    'image-qsj-painting-098': 'La Reddition de Breda',
    'image-qsj-painting-rank-011': 'Le Baiser',
    'image-qsj-painting-rank-012': 'La Jeune Fille à la perle',
    'image-qsj-painting-rank-014': 'La Naissance de Vénus',
    'image-qsj-painting-rank-021': 'La Liberté guidant le peuple',
    'image-qsj-painting-rank-025': 'Le Radeau de La Méduse',
    'image-qsj-painting-rank-027': 'La Ronde de nuit',
    'image-qsj-painting-rank-066': 'Le Concert',
    'image-qsj-painting-rank-076': 'La Naissance de Vénus',
    'image-qsj-painting-rank-100': 'Œillet, lis, lis, rose',
    'image-qsj-painting-rank-039': 'L’Ange déchu',
    'image-qsj-painting-rank-099': 'La Naissance de Vénus',
    'image-qsj-painting-rank-030': 'Le Chien',
    'image-qsj-painting-rank-051': 'Méduse',
    'image-qsj-painting-rank-071': 'Le Massacre de Chios',
    'image-qsj-sculpture-002': 'La Vestale voilée',
    'image-qsj-sculpture-006': 'Apollon et Daphné',
    'image-qsj-sculpture-007': 'L’Extase de sainte Thérèse',
    'image-qsj-sculpture-011': 'La Vierge voilée',
    'image-qsj-sculpture-013': 'La Madone de Bruges',
    'image-qsj-sculpture-015': 'L’Ombre',
    'image-qsj-sculpture-018': 'Le Mémorial Adams',
    'image-qsj-sculpture-036': 'La Vénus de Willendorf',
    'image-qsj-sculpture-037': 'Persée tenant la tête de Méduse',
    'image-qsj-sculpture-030': 'Les Trois Grâces',
    'image-qsj-sculpture-057': 'Oiseau dans l’espace',
    'image-qsj-sculpture-061': 'L’Homme au nez cassé',
    'image-qsj-sculpture-063': 'Le Faune Barberini',
    'image-qsj-sculpture-064': 'L’Homme qui marche',
    'image-qsj-sculpture-065': 'Les Bourgeois de Calais',
    'image-qsj-sculpture-078': 'Le Gladiateur Borghèse',
    'image-qsj-sculpture-060': 'L’Ouvrier et la Kolkhozienne',
    'image-qsj-building-021': 'Taipei 101',
    'image-qsj-building-023': 'Tour de la Perle de l’Orient',
    'image-qsj-building-025': 'The Shard',
    'image-qsj-building-027': 'One World Trade Center',
    'image-qsj-building-028': 'Château Hearst',
    'image-qsj-building-029': 'Édifice Metropolis',
    'image-qsj-building-031': 'Kunsthaus de Graz',
    'image-qsj-building-032': 'Pont de Brooklyn',
    'image-qsj-building-035': '30 St Mary Axe',
    'image-qsj-building-036': 'Casa Milà',
    'image-qsj-building-037': 'Tours Petronas',
    'image-qsj-building-038': 'Flatiron Building',
    'image-qsj-building-039': 'Maison du port d’Anvers',
    'image-qsj-building-040': 'Stade national de Pékin',
    'image-qsj-building-043': 'Basilique du Sacré-Cœur',
    'image-qsj-building-044': 'Pont de l’Øresund',
    'image-qsj-building-045': 'Musée d’art de Milwaukee',
    'image-qsj-building-048': 'Maison dansante',
    'image-qsj-building-049': 'Cathédrale Saint-Paul de Londres',
    'image-qsj-building-050': 'Palais de Westminster',
    'image-qsj-building-052': 'Sainte-Sophie',
    'image-qsj-building-058': 'Château de Neuschwanstein',
    'image-qsj-building-056': 'Château de Versailles',
    'image-qsj-building-059': 'Cathédrale Basile-le-Bienheureux',
    'image-qsj-building-061': 'Cathédrale de Milan',
    'image-qsj-building-066': 'Casa Batlló',
    'image-qsj-building-069': 'Maison Schröder de Rietveld',
    'image-qsj-building-072': 'Musée Guggenheim de Bilbao',
    'image-qsj-building-073': 'Philharmonie de Berlin',
    'image-qsj-building-076': 'Tokyo Skytree',
    'image-qsj-building-077': 'Tour CN',
    'image-qsj-building-079': 'Mémorial de Lincoln',
    'image-qsj-building-080': 'Arche de Gateway',
    'image-qsj-building-082': 'Grande Mosquée de Djenné',
    'image-qsj-building-083': 'Palais du Potala',
    'image-qsj-building-086': 'Pyramide du Soleil de Teotihuacan',
    'image-qsj-building-088': 'Mosquée bleue',
    'image-qsj-building-091': 'Parlement hongrois',
    'image-qsj-building-092': 'Opéra d’Oslo',
    'image-qsj-building-095': 'Tour de Belém',
    'image-qsj-building-097': 'Monticello',
    'image-qsj-building-022': 'Empire State Building',
    'image-qsj-building-055': 'Basilique Saint-Pierre',
    'image-qsj-building-074': 'Burj al-Arab',
    'image-qsj-building-090': 'Église du Saint-Sépulcre',
    'image-qsj-building-024': 'Lloyd’s Building',
    'image-qsj-building-053': 'Panthéon de Rome',
}

data = json.loads(BANK.read_text(encoding='utf-8'))
by_id = {q['id']: q for q in data['questions']}
changed = 0
reveal_names = 0
for qid, french in NAMES.items():
    q = by_id.get(qid)
    if not q:
        continue
    facts = q.setdefault('imageFacts', {})
    facts['frenchTitle'] = french
    if french.casefold() not in {a.casefold() for a in q.get('answers', [])}:
        q.setdefault('answers', []).append(french)
    changed += 1
    reveal_line = f'Titre français : {french}.'
    explanation = q.get('explanation') or ''
    if reveal_line not in explanation:
        q['explanation'] = (explanation.rstrip() + ('\n\n' if explanation.strip() else '') + reveal_line)
        reveal_names += 1
if changed:
    revisions = data.setdefault('revisionHistory', [])
    if not any(x.get('revision') == 'image-qsj-french-names-2026-10-27' for x in revisions):
        revisions.append({'revision': 'image-qsj-french-names-2026-10-27',
            'summary': f'Added French titles and accepted French name variants to {changed} paintings, sculptures, and buildings.'})
    if not any(x.get('revision') == 'image-qsj-french-answer-reveals-2026-10-27' for x in revisions):
        revisions.append({'revision': 'image-qsj-french-answer-reveals-2026-10-27',
            'summary': f'Showed the French title on answer reveal for {reveal_names} image-backed art/site entries.'})
    BANK.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'French titles updated: {changed}/{len(NAMES)} entries matched; answer reveals enriched: {reveal_names}')
