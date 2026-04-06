#!/usr/bin/env python3
"""
systemai_orchestrator.py - Master Coordinator

Loads all 227 modules in the correct dependency order, provides health
monitoring, auto-healing on errors, and dynamic module loading.
"""

import logging
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Ensure repo root is on sys.path so sibling modules are importable
REPO_ROOT = Path(__file__).parent.resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
AICORE_PATH = REPO_ROOT / "aicore"
if str(AICORE_PATH) not in sys.path:
    sys.path.insert(0, str(AICORE_PATH))

from module_loader import ModuleLoader
from health_monitor import HealthMonitor

logger = logging.getLogger(__name__)


class SystemAIOrchestrator:
    """
    Master coordinator for all 227 Python fragments.

    Responsibilities
    ----------------
    - Load all modules via ModuleLoader
    - Register them with HealthMonitor
    - Run periodic auto-healing (re-attempt failed loads)
    - Expose status information to the REST server
    """

    def __init__(self, heal_interval: int = 60, health_check_interval: int = 30):
        self.loader = ModuleLoader()
        self.monitor = HealthMonitor(check_interval=health_check_interval)
        self._heal_interval = heal_interval
        self._stop_event = threading.Event()
        self._heal_thread: Optional[threading.Thread] = None
        self._startup_time: Optional[str] = None
        self._initialized = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> dict:
        """
        Full startup sequence:
        1. Load all modules
        2. Register results with health monitor
        3. Start background monitoring + auto-heal loop
        """
        logger.info("=" * 60)
        logger.info("SystemAI Orchestrator - startup")
        logger.info("=" * 60)

        self._startup_time = datetime.now(timezone.utc).isoformat()

        # Step 1 – load
        metadata = self.loader.load_all()

        loaded = sum(1 for m in metadata.values() if m["status"] == "loaded")
        failed = sum(1 for m in metadata.values() if m["status"] == "failed")

        logger.info("Modules loaded : %d", loaded)
        logger.info("Modules failed : %d", failed)

        # Step 2 – register with health monitor
        self.monitor.register_all(metadata)
        self.monitor.start()

        # Step 3 – background auto-heal
        self._stop_event.clear()
        self._heal_thread = threading.Thread(
            target=self._heal_loop, daemon=True, name="AutoHeal"
        )
        self._heal_thread.start()

        self._initialized = True
        logger.info("Orchestrator ready.")
        return {"loaded": loaded, "failed": failed, "total": len(metadata)}

    def stop(self) -> None:
        logger.info("Orchestrator shutting down …")
        self._stop_event.set()
        self.monitor.stop()
        if self._heal_thread:
            self._heal_thread.join(timeout=5)
        logger.info("Orchestrator stopped.")

    # ------------------------------------------------------------------
    # Auto-healing
    # ------------------------------------------------------------------

    def _heal_loop(self) -> None:
        """Periodically retry modules that failed to load."""
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._heal_interval)
            if self._stop_event.is_set():
                break
            self._attempt_heal()

    def _attempt_heal(self) -> None:
        failed_keys = [
            key
            for key, meta in self.loader.metadata.items()
            if meta["status"] in ("failed", "timeout")
        ]
        if not failed_keys:
            return

        logger.info("Auto-heal: retrying %d failed module(s).", len(failed_keys))
        for key in failed_keys:
            path = self.loader.metadata[key]["path"]
            self.loader.clear_module_state(key)
            self.loader._load_file(path)
            new_status = self.loader.metadata.get(key, {}).get("status", "failed")
            self.monitor.register_module(key, path, new_status)
            if new_status == "loaded":
                logger.info("Auto-heal SUCCESS: %s", key)

    # ------------------------------------------------------------------
    # Dynamic module loading
    # ------------------------------------------------------------------

    def load_module(self, path: str) -> dict:
        """Dynamically load a single module file at runtime."""
        self.loader._load_file(path)
        key = self.loader._path_to_key(path)
        meta = self.loader.metadata.get(key, {"status": "unknown", "path": path})
        self.monitor.register_module(key, path, meta["status"])
        return meta

    def reload_module(self, key: str) -> dict:
        """Force-reload a module by its key."""
        meta = self.loader.metadata.get(key)
        if meta is None:
            return {"error": f"Unknown module: {key}"}
        path = meta["path"]
        self.loader.clear_module_state(key)
        self.loader._load_file(path)
        new_meta = self.loader.metadata.get(key, {"status": "unknown", "path": path})
        self.monitor.register_module(key, path, new_meta["status"])
        return new_meta

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        health_summary = self.monitor.get_summary()
        return {
            "startup_time": self._startup_time,
            "initialized": self._initialized,
            "modules": {
                "total": len(self.loader.metadata),
                "loaded": self.loader.loaded_count,
                "failed": self.loader.failed_count,
            },
            "health": health_summary,
        }

    def list_modules(self, status_filter: Optional[str] = None) -> list[dict]:
        result = []
        for key, meta in self.loader.metadata.items():
            if status_filter and meta["status"] != status_filter:
                continue
            result.append({"key": key, **meta})
        return result


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------
_instance: Optional[SystemAIOrchestrator] = None


def get_orchestrator() -> SystemAIOrchestrator:
    global _instance
    if _instance is None:
        _instance = SystemAIOrchestrator()
    return _instance


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s - %(message)s",
    )
    orch = SystemAIOrchestrator()
    result = orch.start()
    print(f"\n✅  Loaded : {result['loaded']}")
    print(f"❌  Failed : {result['failed']}")
    print(f"📦  Total  : {result['total']}")
    time.sleep(2)
    orch.stop()
