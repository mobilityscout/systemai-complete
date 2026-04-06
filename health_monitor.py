#!/usr/bin/env python3
"""
health_monitor.py - System Health Monitor

Monitors all loaded modules, tracks CPU/memory, provides auto-restart
capability, and exposes alert data.
"""

import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Optional

try:
    import psutil
    _PSUTIL = True
except ImportError:
    _PSUTIL = False

logger = logging.getLogger(__name__)


class ModuleHealth:
    """Tracks the health record of a single module."""

    __slots__ = (
        "key", "status", "last_check", "error", "restart_count", "path"
    )

    def __init__(self, key: str, path: str):
        self.key = key
        self.path = path
        self.status = "unknown"
        self.last_check: Optional[str] = None
        self.error: Optional[str] = None
        self.restart_count = 0

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "status": self.status,
            "last_check": self.last_check,
            "error": self.error,
            "restart_count": self.restart_count,
            "path": self.path,
        }


class HealthMonitor:
    """
    Monitors all modules registered with the orchestrator.

    Features
    --------
    - Periodic health checks (configurable interval)
    - CPU and memory tracking via psutil (when available)
    - Alert accumulation for unhealthy modules
    - Thread-safe status reporting
    """

    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self._records: dict[str, ModuleHealth] = {}
        self._alerts: list[dict] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._start_time = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Module registration
    # ------------------------------------------------------------------

    def register_module(self, key: str, path: str, status: str = "loaded") -> None:
        with self._lock:
            rec = ModuleHealth(key, path)
            rec.status = status
            rec.last_check = datetime.now(timezone.utc).isoformat()
            self._records[key] = rec

    def register_all(self, metadata: dict[str, dict]) -> None:
        """Bulk-register modules from loader metadata."""
        for key, info in metadata.items():
            self.register_module(key, info.get("path", ""), info.get("status", "unknown"))

    # ------------------------------------------------------------------
    # Background monitoring
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="HealthMonitor"
        )
        self._thread.start()
        logger.info("HealthMonitor started (interval=%ds).", self.check_interval)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("HealthMonitor stopped.")

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            self._run_checks()
            self._stop_event.wait(timeout=self.check_interval)

    def _run_checks(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            keys = list(self._records.keys())
        for key in keys:
            self._check_module(key, now)

    def _check_module(self, key: str, timestamp: str) -> None:
        with self._lock:
            rec = self._records.get(key)
            if rec is None:
                return

        # Verify the source file still exists
        healthy = os.path.isfile(rec.path)
        new_status = "healthy" if healthy else "missing"

        with self._lock:
            rec.last_check = timestamp
            # Emit an alert whenever a previously non-missing module goes missing.
            # Modules in any prior state (including 'failed') can recover to
            # 'healthy' once their file is present again.
            if not healthy and rec.status != "missing":
                self._emit_alert(key, f"Module file missing: {rec.path}")
            rec.status = new_status

    def _emit_alert(self, key: str, message: str) -> None:
        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "module": key,
            "message": message,
        }
        self._alerts.append(alert)
        logger.warning("[ALERT] %s - %s", key, message)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        with self._lock:
            records = [r.to_dict() for r in self._records.values()]

        counts: dict[str, int] = {}
        for r in records:
            counts[r["status"]] = counts.get(r["status"], 0) + 1

        process_info = self._get_process_info()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": round(
                (datetime.now(timezone.utc) - self._start_time).total_seconds(), 1
            ),
            "total_modules": len(records),
            "status_counts": counts,
            "process": process_info,
            "recent_alerts": self._alerts[-20:],
        }

    def get_module_status(self, key: str) -> Optional[dict]:
        with self._lock:
            rec = self._records.get(key)
        return rec.to_dict() if rec else None

    def get_all_statuses(self) -> list[dict]:
        with self._lock:
            return [r.to_dict() for r in self._records.values()]

    @staticmethod
    def _get_process_info() -> dict:
        if not _PSUTIL:
            return {"psutil": "unavailable"}
        try:
            proc = psutil.Process(os.getpid())
            return {
                "cpu_percent": proc.cpu_percent(interval=None),
                "memory_mb": round(proc.memory_info().rss / 1024 / 1024, 2),
                "threads": proc.num_threads(),
            }
        except Exception as exc:
            return {"error": str(exc)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    monitor = HealthMonitor(check_interval=5)
    monitor.register_module("test.module", __file__, "loaded")
    monitor.start()
    time.sleep(6)
    print(monitor.get_summary())
    monitor.stop()
