"""Install/update local package archives directly on a USB-connected debug tablet.

Usage: python build/install-tablet-packages.py --serial R52WB0GQRBW
The app is stopped during installation. Unrelated packages are preserved.
"""
import argparse
import json
import re
import subprocess
import tarfile
import tempfile
import time
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
APP = 'com.example.triviaparty'

def prepare_catalog(destination, package_directory=None):
    ids = []
    question_ids = set()
    for archive in sorted((package_directory or ROOT / 'game-library/current').rglob('*.zip')):
        with zipfile.ZipFile(archive) as source:
            manifest = json.loads(source.read('game.json'))
            package_id = manifest['id']
            if not re.fullmatch(r'[A-Za-z0-9_-]+', package_id) or package_id in ids:
                raise ValueError(f'Invalid or duplicate package ID: {package_id}')
            questions = [q for bank_id in manifest['categoryPackages']
                         for q in json.loads(source.read(f'question-bank/{bank_id}.json'))['questions']]
            if not 5 <= len(questions) <= 7:
                raise ValueError(f'{package_id}: packages must have 5–7 questions, found {len(questions)}')
            for question in questions:
                if question['id'] in question_ids:
                    raise ValueError(f'Duplicate question ID: {question["id"]}')
                question_ids.add(question['id'])
            target = destination / package_id
            target.mkdir()
            for member in source.infolist():
                path = PurePosixPath(member.filename.replace('\\', '/'))
                if path.is_absolute() or '..' in path.parts or ':' in str(path):
                    raise ValueError(f'Unsafe ZIP path in {archive.name}')
                output = target.joinpath(*path.parts)
                if member.is_dir():
                    output.mkdir(parents=True, exist_ok=True)
                else:
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(source.read(member))
            ids.append(package_id)
    return ids

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--adb', default='H:/Android/Sdk/platform-tools/adb.exe')
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('--package-dir', type=Path, help='Install only archives in this directory.')
    parser.add_argument('--review-file', type=Path, help='Install an explicitly processed host-review snapshot.')
    args = parser.parse_args()
    def adb(*command):
        return subprocess.check_output([args.adb, '-s', args.serial, *command], text=True, encoding='utf-8').strip()
    with tempfile.TemporaryDirectory(prefix='triviaparty-packages-') as temporary:
        folder = Path(temporary)
        catalog = folder / 'catalog'
        catalog.mkdir()
        ids = prepare_catalog(catalog, args.package_dir)
        source_directory = args.package_dir or ROOT / 'game-library/current'
        migration_file = source_directory / 'MIGRATION.json'
        migration = json.loads(migration_file.read_text(encoding='utf-8')) if migration_file.exists() else {}
        retired = migration.get('retiredPackageIds', [])
        if any(not re.fullmatch(r'[A-Za-z0-9_-]+', pid) or pid in ids for pid in retired):
            raise ValueError('Unsafe or conflicting retirement ID')
        if args.validate_only:
            print(f'Validated {len(ids)} packages.')
            return
        if adb('get-state') != 'device':
            raise RuntimeError('Connect and authorize the tablet first.')
        adb('shell', 'run-as', APP, 'pwd')  # Verify debug access before stopping app.
        stamp = str(time.time_ns())
        stage = 'files/game-packages/.usb-' + stamp
        remote = '/data/local/tmp/trivia-packages-' + stamp + '.tar'
        bundle = folder / 'packages.tar'
        with tarfile.open(bundle, 'w') as tar:
            for package_id in ids:
                tar.add(catalog / package_id, arcname=package_id)
        adb('push', str(bundle), remote)
        adb('shell', 'am', 'force-stop', APP)
        review_data = None
        if args.review_file:
            review_data = json.loads(args.review_file.read_text(encoding='utf-8'))
        elif migration:
            existing_review = adb('shell','run-as',APP,'sh','-c',"'if [ -f files/host-review.json ]; then cat files/host-review.json; fi'")
            if existing_review:
                review_data = json.loads(existing_review)
                usage = review_data.setdefault('usage', {})
                original_usage = dict(usage)
                for pid, sources in migration.get('newPackageSources', {}).items():
                    if pid in usage or not sources: continue
                    plays = min(original_usage.get(source, {}).get('plays', 0) for source in sources)
                    if plays:
                        latest = max(original_usage.get(source, {}).get('lastPlayed', 0) for source in sources
                                     if original_usage.get(source, {}).get('plays', 0) == plays)
                        usage[pid] = dict(plays=plays,lastPlayed=latest)
        commands = [f'mkdir -p {stage}', f'tar -xf {remote} -C {stage}']
        # Install each ID atomically; retain previous directories as hidden backups.
        for package_id in ids:
            destination = 'files/game-packages/' + package_id
            backup = 'files/game-packages/.previous-' + stamp + '-' + package_id
            commands.append(f'if [ -d {destination} ]; then mv {destination} {backup}; fi')
            commands.append(f'mv {stage}/{package_id} {destination}')
        commands.append(f'rmdir {stage}')
        for package_id in retired:
            destination = 'files/game-packages/' + package_id
            backup = 'files/game-packages/.retired-' + stamp + '-' + package_id
            commands.append(f'if [ -d {destination} ]; then mv {destination} {backup}; fi')
        # Keep each Windows command below its command-line length limit.
        for start in range(0, len(commands), 12):
            adb('shell', 'run-as', APP, 'sh', '-c', "'set -e; " + '; '.join(commands[start:start + 12]) + "'")
        for package_id in ids:
            installed = json.loads(adb('shell', 'run-as', APP, 'cat', f'files/game-packages/{package_id}/game.json'))
            if installed['id'] != package_id:
                raise RuntimeError(f'Verification failed: {package_id}')
        if review_data is not None:
            review_copy = folder / 'host-review.json'
            review_copy.write_text(json.dumps(review_data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            review_remote = '/data/local/tmp/trivia-review-' + stamp + '.json'
            adb('push',str(review_copy),review_remote)
            adb('shell','run-as',APP,'cp',review_remote,'files/host-review.json')
            verified_review = json.loads(adb('shell','run-as',APP,'cat','files/host-review.json'))
            if verified_review['reviews'] != review_data['reviews']:
                raise RuntimeError('Question reviews did not survive migration')
            adb('shell','rm',review_remote)
        adb('shell', 'rm', remote)
        adb('shell', 'am', 'start', '-n', APP + '/.MainActivity')
        print(f'Installed/updated and verified {len(ids)} packages; retired {len(retired)} obsolete package IDs. Previous versions retained as hidden backups; question reviews preserved.')

if __name__ == '__main__':
    main()
