#!/usr/bin/env python3
"""Simple launcher interface for Exposome CV Modifier Dashboard.

Usage:
    python run_dashboard.py
    python run_dashboard.py --port 8502 --host 0.0.0.0 --no-browser
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch the Exposome CV Modifier Dashboard (Streamlit)."
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8501, help="Port to bind.")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Disable auto-opening a browser tab.",
    )
    return parser.parse_args()


def ensure_streamlit_available() -> None:
    if shutil.which("streamlit") is None:
        print(
            "ERROR: 'streamlit' executable is not available.\n"
            "Install dependencies first: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)


def main() -> None:
    args = parse_args()
    ensure_streamlit_available()

    app_path = Path(__file__).resolve().parent / "app.py"
    cmd = [
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        args.host,
        "--server.port",
        str(args.port),
        "--server.headless",
        "true" if args.no_browser else "false",
    ]

    print(
        f"Starting Exposome CV Modifier Dashboard on http://{args.host}:{args.port}\n"
        "Press Ctrl+C to stop."
    )
    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
