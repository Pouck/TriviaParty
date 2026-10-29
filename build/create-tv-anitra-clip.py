"""Encode the first 32.2 seconds of CC0 Anitra's Dance for Cast TV playback."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "build" / "audio-tools"))
import imageio_ffmpeg

source = root / "build" / "classic-audio" / "anitra-dance-source.ogg"
target = root / "app" / "src" / "main" / "assets" / "tv" / "music" / "anitra-dance.mp3"
target.parent.mkdir(parents=True, exist_ok=True)
subprocess.run(
    [imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
     "-t", "32.2", "-vn", "-ar", "44100", "-ac", "2", "-codec:a", "libmp3lame", "-b:a", "160k", str(target)],
    check=True,
)
print(f"Created {target}")
