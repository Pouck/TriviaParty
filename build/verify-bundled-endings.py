from pathlib import Path
import json,hashlib,wave,subprocess,sys
R=Path.cwd();sys.path.insert(0,str(R/'build/audio-tools'));import imageio_ffmpeg
rows=json.loads((R/'audio-bank/game-ending-sounds.json').read_text(encoding='utf8'));assert len(rows)==7
for r in rows:
 p=R/'app/src/main/assets/tv/sounds'/r['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 info=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-i',str(p)],capture_output=True,text=True)
 assert '00:00:24.' in info.stderr,(r['file'],info.stderr[:200])
assert (R/'cast-receiver/receiver.js').read_bytes()==(R/'app/src/main/assets/tv/receiver.js').read_bytes()
p=R/'cast-receiver/README.md';s=p.read_text(encoding='utf8');s+='\n## Rotating winner music\n\nEach new game selects one of seven classical 24-second endings on the host. All seven are used in random order before the cycle repeats, with no immediate repeat across cycles. The selected file travels in `TvState.gameEndSoundClip`, so local displays and Cast use the same ending. Single and tied winners share the same behavior. Repeated final-state updates and late connections do not replay the music. Recording credits and licenses are available at `/tv/winner-music-credits` and in `audio-bank/game-ending-sounds.json`.\n\nCategory-intro edition numbers stay attached to the preceding title line, including titles with a dash before the number.\n';p.write_text(s,encoding='utf8')
print('Verified 7 bundled 24-second recordings and byte-identical local/Cast receiver scripts.')
