"""Small adb smoke-test helper using the current visible accessibility tree."""
import subprocess,sys,re
from pathlib import Path
from xml.etree import ElementTree as ET
sys.stdout.reconfigure(encoding='utf-8')
ADB='H:/Android/Sdk/platform-tools/adb.exe'; SERIAL='adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp'
def adb(*args): return subprocess.check_output([ADB,'-s',SERIAL,*args],text=True)
def snapshot():
    for attempt in range(3):
        result=adb('shell','uiautomator','dump','/data/local/tmp/trivia-smoke.xml')
        if 'dumped' in result: break
    else: raise RuntimeError(result)
    adb('pull','/data/local/tmp/trivia-smoke.xml','build/pixel-ui.xml')
    return ET.parse('build/pixel-ui.xml').getroot()
action=sys.argv[1]
if action=='shot':
    adb('shell','screencap','-p','/data/local/tmp/trivia-smoke.png')
    print(adb('pull','/data/local/tmp/trivia-smoke.png','build/'+sys.argv[2]+'.png'))
else:
    nodes=list(snapshot().iter('node'))
    if action=='tap':
        target=next((n for n in nodes if n.get('text')==sys.argv[2]),None)
        if target is None: raise RuntimeError('Visible control not found: '+sys.argv[2])
        x1,y1,x2,y2=map(int,re.findall(r'\d+',target.get('bounds')))
        print(adb('shell','input','tap',str((x1+x2)//2),str((y1+y2)//2)))
    else:
        for n in nodes:
            if n.get('text'): print(n.get('text'),n.get('bounds'))
