from pathlib import Path
s=Path('build/extract-oscar-dialogues.py').read_text(encoding='utf8').replace("build/dialogue-extracts/oscar'","build/dialogue-extracts/oscar-amant'").replace('oscar-02-augmentation.mp3','oscar-05-amant.mp3');Path('build/extract-oscar-amant-dialogues.py').write_text(s,encoding='utf8')
