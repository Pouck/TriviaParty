"""Generate the shared original feedback bank, including the spring buzzer."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name('generate-feedback-sounds.py')))
