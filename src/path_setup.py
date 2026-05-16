"""Ensure project root is on sys.path (for scripts and IDE analysis)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def ensure_project_root() -> Path:
    root = str(PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    return PROJECT_ROOT


def ensure_project_cwd() -> Path:
    root = ensure_project_root()
    os.chdir(root)
    return root
