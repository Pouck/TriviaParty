"""Smoke check the Pixel setup controls using the observed accessibility tree."""
from pathlib import Path
from xml.etree import ElementTree as ET
import subprocess,re,json,sys
sys.stdout.reconfigure(encoding='utf8')
adb=['H:/Android/Sdk/platform-tools/adb.exe','-s',sys.argv[1] if len(sys.argv)>1 else '192.168.86.47:34065']
def run(*a):return subprocess.check_output(adb+list(a),timeout=20)
def tree():
 run('shell','uiautomator','dump','/data/local/tmp/trivia-smoke.xml')
 data=run('exec-out','cat','/data/local/tmp/trivia-smoke.xml');Path('build/pixel-ui.xml').write_bytes(data);return list(ET.fromstring(data).iter('node'))
def tap(label):
 nodes=tree();node=next((n for n in nodes if n.get('text')==label),None)
 if node is None:raise ValueError('Not visible: '+label)
 a,b,c,d=map(int,re.findall(r'\d+',node.get('bounds')));run('shell','input','tap',str((a+c)//2),str((b+d)//2))
if any(n.get('text')=='Annuler' for n in tree()):tap('Annuler')
tap('Tests');texts=[n.get('text') for n in tree() if n.get('text')];assert any(re.match(r'[1-9][0-9]* forfaits? · [1-9][0-9]* questions',t) for t in texts),texts
print('Tests button auto-selected:',next(t for t in texts if re.match(r'[1-9][0-9]* forfaits? ·',t)))
tap('Manuel');texts=[n.get('text') for n in tree() if n.get('text')];assert 'Tous' in texts;assert 'Tout sélectionner' in texts;assert 'Rechercher un forfait' in texts
Path('build/pixel-manual-redesign.png').write_bytes(run('exec-out','screencap','-p'))
# Choose the first visible subject chip by its actual text; confirm its bulk selection is available.
subject=next((t for t in texts if t in ('Architecture','Arts','Géographie','Histoire')),None)
if subject:
 tap(subject);nodes=tree();assert any(n.get('text')=='Tout sélectionner' for n in nodes);tap('Tout sélectionner');texts=[n.get('text') for n in tree() if n.get('text')];assert 'Tout retirer' in texts
 print('Manual category filter and bulk selection work:',subject)
tap('Tirage');assert any(n.get('text')=='6 × 1' for n in tree());tap('Tirer les forfaits');texts=[n.get('text') for n in tree() if n.get('text')];assert any(t.startswith('6 forfaits ·') for t in texts),texts
print('Default 6 × 1 draws six packages without starting a game.')
print('Setup controls verified; no game launched.')
