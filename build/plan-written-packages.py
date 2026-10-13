"""Keep oral sets while converting approximately half of each subject's free-answer sets."""
import collections,json,pathlib,random
root=pathlib.Path('game-library/current');catalog=json.loads((root/'CATALOGUE.json').read_text(encoding='utf8'))
groups=collections.defaultdict(list)
for package in catalog:
    if package['test']:continue
    bank=json.loads((root/'sources'/package['id']/'question-bank'/f'{package["id"]}.json').read_text(encoding='utf8'))
    kind=bank['questions'][0]['kind']
    if kind in ['textAnswer','guessWho']:groups[(bank['subject'],kind)].append(package['id'])
selected=[]
for group,ids in sorted(groups.items()):
    ids.sort();random.Random(str(group)+'written-20261012').shuffle(ids)
    selected+=ids[:len(ids)//2]
pathlib.Path('game-library/WRITTEN-PACKAGES.json').write_text(json.dumps(sorted(selected),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(selected),'written packages planned;',sum(map(len,groups.values()))-len(selected),'oral packages retained.')
