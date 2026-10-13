from pathlib import Path
from collections import Counter
import csv, json, zipfile
from quiz_choice_order import randomize_choices
from culture_guess_who_data import PACKAGES as GUESS_WHO
from culture_multiple_choice_data import PACKAGES as MULTIPLE_CHOICE

root = Path('package-examples/culture-2026-10-10')
root.mkdir(parents=True, exist_ok=True)
clue_rows, choice_rows, catalog = [], [], []
all_ids, positions = set(), Counter()
for mode, packages in [('qsj',GUESS_WHO),('qcm',MULTIPLE_CHOICE)]:
    for package_index,(slug,(title,entries)) in enumerate(packages.items()):
        package_id = f'culture-{mode}-{slug}-20261010'
        assert len(package_id) <= 64
        name = ('Qui suis-je ? — ' if mode == 'qsj' else '') + title
        flips = 3 if mode == 'qsj' else 2
        points = 20 if mode == 'qsj' else 15
        game = dict(id=package_id,name=name,description=f'{len(entries)} questions en français. '+('4 indices de 20 secondes ; 20 → 15 → 10 → 5 points ; erreur : −5 points.' if mode=='qsj' else '15 secondes ; 15 → 10 → 5 points.'),categoryPackages=[package_id],answerTimeSeconds=10,timingConfig=dict(secondsPerFlip=20 if mode=='qsj' else 5,decayPercentagePerFlip=0.0,maxFlips=flips,pointsDecayPerFlip=5))
        questions = []
        for number,entry in enumerate(entries,1):
            question_id = f'{package_id}-{number:02d}'
            assert question_id not in all_ids
            all_ids.add(question_id)
            common = dict(id=question_id,category=name,basePoints=points,penaltyPoints=5 if mode=='qsj' else 0)
            if mode == 'qsj':
                # Manual host validation: only the canonical answer is displayed on reveal.
                questions.append(dict(kind='guessWho',**common,prompt='Qui suis-je ?',clues=entry['clues'],acceptableAnswers=entry['acceptableAnswers'][:1]))
                clue_rows.append([name,number,*entry['clues'],entry['acceptableAnswers'][0],' / '.join(entry['acceptableAnswers'][1:])])
            else:
                prompt,options,correct,explanation = entry
                questions.append(dict(kind='multipleChoice',**common,prompt=prompt,options=[f'{letter} — {option}' for letter,option in zip('ABCD',options)],correctOptionIndex=correct))
        if mode == 'qcm':
            extras = [(0,1),(2,3),(0,2),(1,3),(0,1)][package_index]
            randomize_choices(questions,package_id,extra_positions=extras)
            count = Counter(q['correctOptionIndex'] for q in questions)
            assert sorted(count.values()) == [2,2,3,3]
            positions.update(count)
            for number,(question,entry) in enumerate(zip(questions,entries),1):
                choice_rows.append([name,number,question['prompt'],*question['options'],question['options'][question['correctOptionIndex']],entry[3]])
        category = dict(category=name,answerMode='BUZZER' if mode=='qsj' else 'SIMULTANEOUS',questionTypes=['Qui suis-je ?' if mode=='qsj' else 'Choix multiples'],questions=questions)
        source = root/'sources'/package_id
        for relative,data in [('game.json',game),(f'question-bank/{package_id}.json',category)]:
            file=source/relative
            file.parent.mkdir(parents=True,exist_ok=True)
            file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        archive = root/f'culture-{mode}-{slug}.zip'
        with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
            for file in sorted(source.rglob('*.json')): z.write(file,file.relative_to(source).as_posix())
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            assert len(z.namelist()) == 2
        catalog.append((archive.name,name,len(questions),mode))

for filename,headers,rows in [
 ('QUI-SUIS-JE-ET-CORRIGE.csv',['Catégorie','Question','Indice 1','Indice 2','Indice 3','Indice 4','Réponse','Autres formulations acceptables par l’hôte'],clue_rows),
 ('CHOIX-MULTIPLES-ET-CORRIGE.csv',['Catégorie','Question','Texte','A','B','C','D','Bonne réponse','Explication'],choice_rows)]:
    with (root/filename).open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f,delimiter=';'); writer.writerow(headers); writer.writerows(rows)

assert len(catalog)==19 and len(clue_rows)==36 and len(choice_rows)==50 and len(all_ids)==86
assert positions == Counter({0:13,1:13,2:12,3:12})
lines = ['# Forfaits — Antiquité, mythologie et littérature','','19 forfaits indépendants : 36 questions à indices et 50 questions à choix multiples. Tous sont en français.','','## Importation','','Importer chaque ZIP souhaité depuis l’application ; plusieurs forfaits peuvent être sélectionnés pour une partie. Ne pas importer les CSV ou les dossiers de sources. Les forfaits à indices nécessitent la version de l’application prenant en charge « Qui suis-je ? ».','','## Réglages','','- Qui suis-je ? : quatre indices, révélés à 0, 20, 40 et 60 secondes ; 80 secondes au total ; 20 → 15 → 10 → 5 points. Buzzer oral, avec 10 secondes pour répondre après le buzzer ; validation sur le panneau privé d’un second appareil.','- Choix multiples : 15 secondes ; 15 → 10 → 5 points ; réponses simultanées en un clic.','- Qui suis-je ? : −5 points par mauvaise réponse ou délai dépassé ; retour au prochain indice. QCM : aucune pénalité ordinaire. Les mises éventuelles suivent les règles de l’application.','- Les réponses A–D sont mélangées dans chaque archive : deux ou trois bonnes réponses par position sur dix questions. Le mélange ne change pas automatiquement à chaque partie.','','## Archives','','| Forfait | Questions | Format |','| --- | ---: | --- |']
lines += [f'| [{title}]({archive}) | {count} | {"Indices + buzzer" if mode=="qsj" else "Choix multiples"} |' for archive,title,count,mode in catalog]
lines += ['','## Révision et mises à jour','','Voir [les vérifications, corrections et recoupements](VERIFICATION.md), [le corrigé des indices](QUI-SUIS-JE-ET-CORRIGE.csv) et [le corrigé des choix multiples](CHOIX-MULTIPLES-ET-CORRIGE.csv).','','Les sources JSON sont sous `sources/`. Pour mettre à jour un forfait, conserver son identifiant et reconstruire son ZIP avec `game.json` et `question-bank/` à la racine. Pour régénérer les archives, modifier les données dans `build/culture_guess_who_data.py` ou `build/culture_multiple_choice_data.py`, puis exécuter `python build/build-culture-packages.py`.','']
(root/'README.md').write_text('\n'.join(lines),encoding='utf-8')
print(f'{len(catalog)} archives ; {len(clue_rows)} questions à indices ; {len(choice_rows)} QCM ; {len(all_ids)} identifiants uniques. Répartition QCM : {dict(positions)}')
