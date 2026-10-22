from pathlib import Path
import subprocess,sys,json
R=Path.cwd();D=R/'build/dialogue-extracts/vadrouille-prisonnier';W=R/'build/movie-audition'
subprocess.run([str(W/'whisper-bin/Release/whisper-cli.exe'),'-m',str(W/'ggml-base.bin'),'-f',str(D/'source-16k.wav'),'-l','fr','-otxt','-oj','-of',str(D/'transcript-base'),'-t','4'],check=True,capture_output=True)
sys.stdout.reconfigure(encoding='utf8')
for r in json.loads((D/'transcript-base.json').read_text(encoding='utf8'))['transcription']:print(r['offsets'],r['text'])

