"""Verify and atomically activate a reviewed private bank using one transfer."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import tarfile
import time

ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/'build/reviewed-audio-20261024/bank'
ADB='H:/Android/Sdk/platform-tools/adb.exe'
p=argparse.ArgumentParser();p.add_argument('--serial');p.add_argument('--pack-only',action='store_true');args=p.parse_args()
rows=json.loads((BANK/'reactions.json').read_text(encoding='utf-8'))
assert len(rows)==284 and {r['outcome'] for r in rows}=={'good','bad'}
assert len({r['sourceId'] for r in rows})==270
assert all(not r['sourceId'].endswith('20261016-044') for r in rows)
names=[r['file'] for r in rows]+['credits.html','reactions.json']
assert len(set(names))==len(names)
for r in rows:
    assert re.fullmatch(r'(good|bad)-\d{3}\.wav',r['file'])
    assert hashlib.sha256((BANK/r['file']).read_bytes()).hexdigest()==r['sha256']
checksums=''.join(hashlib.sha256((BANK/name).read_bytes()).hexdigest()+'  '+name+'\n' for name in names)
(BANK/'checksums.sha256').write_text(checksums,encoding='ascii')
version=hashlib.sha256((BANK/'reactions.json').read_bytes()).hexdigest()[:16]
archive=BANK.parent/f'bank-{version}.tar.gz'
if not archive.exists():
    with tarfile.open(archive,'w:gz',compresslevel=3) as tar:
        for name in names+['checksums.sha256']:
            tar.add(BANK/name,arcname=name,recursive=False)
print(f'Verified {len(rows)} entries / 270 recordings; archive {archive.stat().st_size/1e6:.1f} MB.',flush=True)
if args.pack_only:
    raise SystemExit
assert args.serial,'--serial required'
def run(*command,timeout=60):
    return subprocess.check_output([ADB,'-s',args.serial,*command],stderr=subprocess.STDOUT,timeout=timeout)
remote=f'/data/local/tmp/reviewed-audio-{version}.tar.gz'
stage=f'files/reaction-preview-stage-{version}'
backup=f'files/reaction-preview-backup-{int(time.time())}'
assert re.fullmatch(r'files/reaction-preview-stage-[0-9a-f]{16}',stage)
print('Transferring reviewed recordings...',flush=True)
print(run('push',str(archive),remote,timeout=600).decode(errors='replace'),flush=True)
run('shell',f'run-as com.example.triviaparty mkdir -p {stage}')
run('shell',f'run-as com.example.triviaparty tar -xzf {remote} -C {stage}',timeout=180)
verified=run('shell',f"run-as com.example.triviaparty sh -c 'cd {stage} && sha256sum -c checksums.sha256'",timeout=180).decode()
assert verified.count(': OK')==len(names),(verified,len(names))
print(f'All {len(names)} installed files verified; activating the bank.',flush=True)
run('shell',f"run-as com.example.triviaparty sh -c 'if [ -d files/reaction-preview ]; then mv files/reaction-preview {backup}; fi; mv {stage} files/reaction-preview'")
actual=run('exec-out','run-as','com.example.triviaparty','cat','files/reaction-preview/reactions.json')
assert actual==(BANK/'reactions.json').read_bytes()
run('shell','rm','-f',remote)
print(f'ACTIVE: private-{version}; prior bank preserved at {backup}. Restart the app to load it.',flush=True)
