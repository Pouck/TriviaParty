"""Read active package metadata and saved reviews without copying hidden backups."""
import io,json,subprocess,tarfile,base64
from pathlib import Path
adb=['H:/Android/Sdk/platform-tools/adb.exe','-s','adb-2B021FDH300B81-JSzzEA._adb-tls-connect._tcp']
raw=subprocess.check_output(adb+['shell','-T','run-as','com.example.triviaparty','sh','-c',
    "'tar -cf - files/game-packages/*/game.json files/game-packages/*/question-bank/*.json | base64'"])
raw=base64.b64decode(raw)
packages={}
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
    for member in tar:
        if not member.isfile():continue
        parts=member.name.split('/');pid=parts[2]
        record=packages.setdefault(pid,{'banks':{}})
        content=tar.extractfile(member).read()
        try: value=json.loads(content)
        except Exception as error: raise RuntimeError(f'{member.name}: {len(content)} bytes; {error}') from error
        if parts[-1]=='game.json':record['game']=value
        else:record['banks'][parts[-1]]=value
Path('build/pixel-library-metadata.json').write_text(json.dumps(packages,ensure_ascii=False,indent=2),encoding='utf-8')
reviews=subprocess.check_output(adb+['shell','run-as','com.example.triviaparty','cat','files/host-review.json'])
Path('build/pixel-reviews-before-resize.json').write_bytes(reviews)
print('Read',len(packages),'active packages and',len(json.loads(reviews)['reviews']),'saved reviews.')
