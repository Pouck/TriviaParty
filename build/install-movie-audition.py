"""Install/remove the private dialogue audition bank without modifying questions or reviews."""
from pathlib import Path
import argparse,subprocess,json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--serial',required=True);p.add_argument('--remove',action='store_true');p.add_argument('--bank',type=Path,default=ROOT/'build/movie-audition');a=p.parse_args()
adb=['H:/Android/Sdk/platform-tools/adb.exe','-s',a.serial]
def run(*args):return subprocess.check_output(adb+list(args),timeout=30,stderr=subprocess.PIPE)
if a.remove:
 run('shell','run-as','com.example.triviaparty','rm','-f','files/reaction-preview/reactions.json')
 print('Preview disabled; restart TriviaParty to restore the standard bank.');raise SystemExit
records=json.loads((a.bank/'reactions.json').read_text(encoding='utf8'))
assert {r['outcome'] for r in records}=={'good','bad'}
for r in records:
 assert re.fullmatch(r'(good|bad)-[0-9]{2,4}\.wav',r['file'])
 assert hashlib.sha256((a.bank/r['file']).read_bytes()).hexdigest()==r['sha256']
run('shell','run-as','com.example.triviaparty','mkdir','-p','files/reaction-preview')
# Read all installed hashes in one call; only transfer changed files, manifest last.
installed={}
try:
 inventory=run('shell',"run-as com.example.triviaparty sh -c 'cd files/reaction-preview && sha256sum *.wav credits.html reactions.json'").decode()
 for line in inventory.splitlines():
  parts=line.split()
  if len(parts)==2 and re.fullmatch('[0-9a-f]{64}',parts[0]):installed[parts[1]]=parts[0]
except subprocess.CalledProcessError:pass
changed=0
for name in [r['file'] for r in records]+['credits.html','reactions.json']:
 if installed.get(name)==hashlib.sha256((a.bank/name).read_bytes()).hexdigest():continue
 changed+=1
 remote='/data/local/tmp/trivia-reaction-'+name
 run('push',str(a.bank/name),remote)
 target='files/reaction-preview/'+name
 run('shell','run-as','com.example.triviaparty','cp',remote,target+'.new')
 run('shell','run-as','com.example.triviaparty','mv',target+'.new',target)
 actual=run('exec-out','run-as','com.example.triviaparty','cat',target)
 assert actual==(a.bank/name).read_bytes(),name
 run('shell','rm',remote)
print(f'Installed and verified {len(records)} private reaction clips ({changed} files transferred). Restart TriviaParty to activate.')
