from pathlib import Path
s=Path('build/extract-oscar-dialogues.py').read_text(encoding='utf8').replace('build/dialogue-extracts/oscar','build/dialogue-extracts/oscar-vole').replace('oscar-02-augmentation.mp3','oscar-04-vole.mp3')
Path('build/extract-oscar-vole-dialogues.py').write_text(s,encoding='utf8')
