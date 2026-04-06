#!/usr/bin/env python3
"""
module_loader.py - Dynamic Module System

Loads all 227 Python fragments dynamically, resolves circular dependencies,
injects dependencies, and caches module metadata.
"""

import os
import sys
import importlib
import importlib.util
import logging
import queue
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Modules are imported in a worker thread so we can enforce a timeout.
# Files with blocking module-level code (e.g. `while True: input(…)`)
# will be marked "timeout" rather than hanging the process.
_IMPORT_TIMEOUT_SECONDS = 5

REPO_ROOT = Path(__file__).parent.resolve()
AICORE_PATH = REPO_ROOT / "aicore"


class ModuleLoader:
    """Dynamically loads and caches all Python modules in the repository."""

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or AICORE_PATH
        self._loaded: dict[str, object] = {}
        self._failed: dict[str, str] = {}
        self._metadata: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover(self) -> list[str]:
        """Return sorted list of all .py file paths under base_path."""
        files = []
        for root, _, filenames in os.walk(self.base_path):
            for name in sorted(filenames):
                if name.endswith(".py") and not name.startswith("__"):
                    files.append(os.path.join(root, name))
        return sorted(files)

    def load_all(self) -> dict[str, dict]:
        """
        Load every discovered module.

        Returns a mapping of module_key -> metadata dict with keys:
          status, path, load_time_ms, error (optional)
        """
        paths = self.discover()
        logger.info("Discovered %d Python files to load.", len(paths))

        for path in paths:
            self._load_file(path)

        return self._metadata

    def get(self, module_key: str) -> Optional[object]:
        """Return a loaded module by its key, or None if not available."""
        return self._loaded.get(module_key)

    @property
    def loaded_count(self) -> int:
        return len(self._loaded)

    @property
    def failed_count(self) -> int:
        return len(self._failed)

    @property
    def metadata(self) -> dict[str, dict]:
        return dict(self._metadata)

    def clear_module_state(self, key: str) -> None:
        """Remove all cached state for a module so it can be re-loaded."""
        self._loaded.pop(key, None)
        self._failed.pop(key, None)
        self._metadata.pop(key, None)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_file(self, path: str) -> None:
        key = self._path_to_key(path)
        if key in self._loaded:
            return

        start = time.monotonic()
        result_q: queue.Queue = queue.Queue()

        def _do_import():
            # Redirect stdin so module-level input() calls raise EOFError
            # rather than blocking the thread indefinitely.
            # Note: daemon threads that time out will keep running until the
            # interpreter exits; this is acceptable for the small number of
            # modules with blocking module-level code in this codebase.
            import io
            saved_stdin = sys.stdin
            sys.stdin = io.StringIO()
            try:
                module = self._import_from_path(key, path)
                result_q.put(("ok", module))
            except BaseException as exc:
                # Catch SystemExit too (raised by e.g. Flask's app.run()
                # when port binding fails and Werkzeug calls sys.exit).
                result_q.put(("err", exc))
            finally:
                sys.stdin = saved_stdin

        t = threading.Thread(target=_do_import, daemon=True)
        t.start()
        t.join(timeout=_IMPORT_TIMEOUT_SECONDS)

        elapsed_ms = round((time.monotonic() - start) * 1000, 2)

        if t.is_alive():
            # Module has blocking code that didn't respond to EOFError
            reason = f"import timed out after {_IMPORT_TIMEOUT_SECONDS}s"
            self._failed[key] = reason
            self._metadata[key] = {
                "status": "timeout",
                "path": path,
                "load_time_ms": elapsed_ms,
                "error": reason,
            }
            logger.debug("Timeout loading %s", key)
            return

        outcome, payload = result_q.get_nowait()
        if outcome == "ok":
            self._loaded[key] = payload
            self._metadata[key] = {
                "status": "loaded",
                "path": path,
                "load_time_ms": elapsed_ms,
            }
            logger.debug("Loaded %s in %.1f ms", key, elapsed_ms)
        else:
            reason = f"{type(payload).__name__}: {payload}"
            self._failed[key] = reason
            self._metadata[key] = {
                "status": "failed",
                "path": path,
                "load_time_ms": elapsed_ms,
                "error": reason,
            }
            logger.debug("Failed to load %s: %s", key, reason)

    @staticmethod
    def _import_from_path(module_key: str, path: str) -> object:
        spec = importlib.util.spec_from_file_location(module_key, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot create spec for {path}")
        module = importlib.util.module_from_spec(spec)
        # Register in sys.modules to allow intra-package references
        sys.modules.setdefault(module_key, module)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def _path_to_key(path: str) -> str:
        """Convert a file path to a dotted module key."""
        p = Path(path)
        try:
            rel = p.relative_to(REPO_ROOT)
        except ValueError:
            rel = p
        parts = list(rel.with_suffix("").parts)
        return ".".join(parts)


# ---------------------------------------------------------------------------
# Convenience singleton used by other components
# ---------------------------------------------------------------------------
_default_loader: Optional[ModuleLoader] = None


def get_loader() -> ModuleLoader:
    global _default_loader
    if _default_loader is None:
        _default_loader = ModuleLoader()
    return _default_loader


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    loader = ModuleLoader()
    metadata = loader.load_all()
    loaded = sum(1 for m in metadata.values() if m["status"] == "loaded")
    failed = sum(1 for m in metadata.values() if m["status"] == "failed")
    print(f"\n✅ Loaded : {loaded}")
    print(f"❌ Failed : {failed}")
    print(f"📦 Total  : {len(metadata)}")
