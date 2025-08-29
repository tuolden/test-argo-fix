"""Production app runner that works without knowing the package name.

This avoids template placeholders in Docker CMD by discovering the package
under src/ at runtime and importing its `main.app` object.
"""
from __future__ import annotations

import importlib
import os
import pkgutil
import sys
from pathlib import Path

import uvicorn


def detect_project_name() -> str:
    """Detect the single top-level package under src/ and return its name.

    Preference order: first package found that is not hidden and not this module.
    """
    src_dir = Path(__file__).resolve().parent
    # src_dir is .../src because this file is placed directly under src/
    # Ensure src is on sys.path (Docker already sets PYTHONPATH=/app/src but keep safe)
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    for m in pkgutil.iter_modules([str(src_dir)]):
        if m.name.startswith("."):
            continue
        if m.name == Path(__file__).stem:
            # Skip this helper module (app_runner)
            continue
        return m.name
    raise RuntimeError("Could not detect project package under src/")


def main() -> None:
    package = detect_project_name()
    module = importlib.import_module(f"{package}.main")
    app = getattr(module, "app", None)
    if app is None:
        raise RuntimeError(f"Module {package}.main does not define 'app'")

    # Default to localhost; allow override via HOST env for containerized deploys
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8080"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    uvicorn.run(app, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    main()

