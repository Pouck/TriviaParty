"""Create MP3 delivery copies for Cast TVs whose media element rejects WAV."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "build" / "audio-tools"))
import imageio_ffmpeg

sounds = root / "app" / "src" / "main" / "assets" / "tv" / "sounds"
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
converted = 0
for source in sorted(sounds.glob("*.wav")):
    target = source.with_suffix(".mp3")
    if target.exists():
        continue
    subprocess.run(
        [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
         "-vn", "-ar", "44100", "-ac", "1", "-codec:a", "libmp3lame", "-b:a", "128k", str(target)],
        check=True,
    )
    converted += 1
print(f"Created {converted} MP3 delivery copies in {sounds}")
