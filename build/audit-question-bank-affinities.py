#!/usr/bin/env python3
"""Compatibility entry point for the current bank cleanup audit."""

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).with_name("audit-question-bank-cleanup.py")), run_name="__main__")
