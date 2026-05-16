"""Deprecated alias — run `python tests/evaluate_agent.py` instead."""

if __name__ == "__main__":
    import runpy
    from pathlib import Path

    from src.path_setup import ensure_project_cwd

    root = ensure_project_cwd()
    runpy.run_path(str(root / "tests" / "evaluate_agent.py"), run_name="__main__")
