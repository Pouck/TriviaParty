from pathlib import Path
import subprocess
import sys
import tempfile
import re
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "build" / "audio-tools"))
import imageio_ffmpeg


ROOT = Path(__file__).resolve().parents[1]
CLIPS = ROOT / "audio-bank" / "clips"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SOURCES = [
    (
        "classical-answer-good.wav",
        "https://upload.wikimedia.org/wikipedia/commons/5/59/Kimiko_Ishizaka_-_J.S._Bach-_-Open-_Goldberg_Variations%2C_BWV_988_%28Piano%29_-_01_Aria.mp3",
        True,
        0.9,
        1.4,
    ),
    (
        "classical-answer-bad.wav",
        "https://upload.wikimedia.org/wikipedia/commons/2/26/Kimiko_Ishizaka_-_J.S._Bach-_-Open-_Goldberg_Variations%2C_BWV_988_%28Piano%29_-_26_Variatio_25_a_2_Clav.mp3",
        False,
        0.9,
        3.0,
    ),
    (
        "classical-answer-bad-alt.wav",
        "https://upload.wikimedia.org/wikipedia/commons/5/50/Kimiko_Ishizaka_-_J.S._Bach-_-Open-_Goldberg_Variations%2C_BWV_988_%28Piano%29_-_16_Variatio_15_a_1_Clav._Canone_alla_Quinta.mp3",
        False,
        0.9,
        3.0,
    ),
]


def make_clip(url: str, output: Path, temp_dir: Path, trim_leading_silence: bool, fade_out: float, duration: float) -> None:
    source = temp_dir / (output.stem + ".mp3")
    request = urllib.request.Request(url, headers={"User-Agent": "TriviaPartyPrivateSampler/1.0"})
    with urllib.request.urlopen(request, timeout=45) as response, source.open("wb") as target:
        target.write(response.read())
    start = 0.0
    if trim_leading_silence:
        probe = subprocess.run(
            [FFMPEG, "-hide_banner", "-i", str(source), "-af", "silencedetect=noise=-42dB:d=0.08", "-f", "null", "NUL"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False,
        )
        match = re.search(r"silence_end:\s*([0-9.]+)", probe.stderr)
        if match:
            start = max(0.0, float(match.group(1)) - 0.015)
    fade_start = duration - fade_out
    subprocess.run(
        [
            FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
            "-af",
            f"atrim=start={start:.3f}:duration={duration},asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-1.5:LRA=7,afade=t=in:st=0:d=0.025,afade=t=out:st={fade_start:.3f}:d={fade_out:.3f}",
            "-ar", "44100", "-ac", "1", "-c:a", "pcm_s16le", str(output),
        ],
        check=True,
    )


def write_sampler() -> None:
    page = ROOT / "audio-bank" / "classical-answer-sampler.html"
    page.write_text("""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Classical answer cues — sampler</title>
<style>
:root{color-scheme:dark;--bg:#101827;--panel:#192437;--line:#34445d;--ink:#f1f5fb;--muted:#b7c4d6;--accent:#8bd5ca;--gold:#ffd385}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 15% 0%,#263755 0,transparent 48%),var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}
main{max-width:900px;margin:auto;padding:36px 22px 70px}h1{font-size:clamp(2rem,5vw,3rem);line-height:1.1;margin:0 0 12px}h2{margin:0;font-size:1.25rem}p{color:var(--muted);margin:.45rem 0}.lede{max-width:740px;font-size:1.08rem}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,340px),1fr));gap:16px;margin:24px 0}.card{background:linear-gradient(140deg,#1c2a40,#151f31);border:1px solid var(--line);border-radius:16px;padding:20px}.tag{display:inline-block;background:#263650;border-radius:99px;padding:3px 10px;color:var(--accent);font-size:.78rem;margin:10px 0}audio{display:block;width:100%;margin:12px 0}.note{border-left:3px solid var(--gold);padding:10px 14px;background:#ffd38512;color:#f8e8c8}a{color:var(--accent)}small{color:#97a8bf}
</style></head><body><main>
<h1>Classical answer cues</h1>
<p class="lede">Short, level-matched Bach piano phrases. The Aria opening is trimmed past its quiet lead-in; the ending of each sample fades smoothly.</p>
<section class="grid">
<article class="card"><h2>Correct · Bach, “Aria”</h2><span class="tag">1.4 seconds · piano</span><p>The first chime and its short decay; the second chime is trimmed away.</p><audio controls preload="metadata" src="clips/classical-answer-good.wav"></audio></article>
<article class="card"><h2>Incorrect · Variation 25</h2><span class="tag">3 seconds · piano · G minor</span><p>The slow, tense phrase you heard before, now with a longer, softer fade-out.</p><audio controls preload="metadata" src="clips/classical-answer-bad.wav"></audio></article>
<article class="card"><h2>Incorrect · Variation 15</h2><span class="tag">3 seconds · piano · G minor</span><p>An alternative minor-key phrase: more restrained and reflective than Variation 25.</p><audio controls preload="metadata" src="clips/classical-answer-bad-alt.wav"></audio></article>
</section>
<p class="note"><strong>Source and reuse:</strong> These recordings are by Kimiko Ishizaka for the Open Goldberg Variations project and are released under CC0. The clips are short, level-matched excerpts prepared for evaluation. <a href="https://commons.wikimedia.org/wiki/Category:Open_Goldberg_Variations">Recording and project details</a> · <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 terms</a>.</p>
<p><small>These are audition samples only; the game’s answer sounds have not been replaced.</small></p>
</main></body></html>
""", encoding="utf-8")


def main() -> None:
    CLIPS.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="triviaparty-answer-cues-") as temp:
        temp_dir = Path(temp)
        refresh = set(sys.argv[1:])
        for filename, url, trim_silence, fade_out, duration in SOURCES:
            output = CLIPS / filename
            if not output.exists() or filename in refresh:
                make_clip(url, output, temp_dir, trim_silence, fade_out, duration)
            print(f"Ready {output.relative_to(ROOT)} ({output.stat().st_size:,} bytes)")
    write_sampler()
    print("Created audio-bank/classical-answer-sampler.html")


if __name__ == "__main__":
    main()
