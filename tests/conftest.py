"""Pytest bootstrap: project root on sys.path for `from src...` imports."""

from src.path_setup import ensure_project_root

ensure_project_root()
