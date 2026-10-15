"""Prepare the current curated private film bank; source audio stays outside Git."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(root/'build/prepare-expanded-movie-bank.py')],check=True)
subprocess.run([sys.executable,str(root/'build/finalize-expanded-movie-bank.py')],check=True)
