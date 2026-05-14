from __future__ import annotations

import runpy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".deps"))
sys.argv = [
    "streamlit",
    "run",
    "app.py",
    "--global.developmentMode",
    "false",
    "--server.port",
    "8501",
    "--server.address",
    "localhost",
    "--server.headless",
    "true",
    "--browser.gatherUsageStats",
    "false",
]

runpy.run_module("streamlit", run_name="__main__")
