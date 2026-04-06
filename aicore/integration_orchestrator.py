#!/usr/bin/env python3
"""
INTEGRATION ORCHESTRATOR
Koordiniert das Zusammenspiel aller 227 Python-Fragmente.
Bietet Lifecycle-Management, Health-Checks und Event-Routing.
"""

import logging
import threading
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime, timezone

from fragment_registry import FragmentRegistry, FragmentInfo, get_registry
from dependency_mapper import DependencyMapper

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Enums & Data classes
# ---------------------------------------------------------------------------


class FragmentState(str, Enum):
    REGISTERED = "registered"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    STOPPED = "stopped"


class OrchestratorEvent:
    """Ein internes Event, das zwischen Fragmenten weitergeleitet wird."""

    def __init__(self, event_type: str, source: str, payload: Dict):
        self.event_type = event_type
        self.source = source
        self.payload = payload
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.handled_by: List[str] = []

    def to_dict(self) -> Dict:
        return {
            "event_type": self.event_type,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "handled_by": self.handled_by,
        }


class FragmentHandle:
    """Laufzeit-Handle für ein aktives Fragment."""

    def __init__(self, info: FragmentInfo):
        self.info = info
        self.state: FragmentState = FragmentState.REGISTERED
        self.module: Optional[Any] = None
        self.error: Optional[str] = None
        self.started_at: Optional[str] = None
        self.event_handlers: Dict[str, Callable] = {}

    @property
    def fragment_id(self) -> str:
        return self.info.id

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        self.event_handlers[event_type] = handler

    def to_dict(self) -> Dict:
        return {
            "fragment_id": self.fragment_id,
            "name": self.info.name,
            "category": self.info.category,
            "state": self.state.value,
            "error": self.error,
            "started_at": self.started_at,
        }

    def __repr__(self) -> str:
        return f"<FragmentHandle id={self.fragment_id!r} state={self.state.value}>"


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class IntegrationOrchestrator:
    """
    Koordiniert das Zusammenspiel aller registrierten Fragmente.

    Funktionen:
    - Lädt Fragmente über die FragmentRegistry
    - Verwaltet den Lifecycle (start / stop / restart)
    - Leitet Events zwischen Fragmenten weiter
    - Überwacht Health-Status
    - Nutzt den DependencyMapper für Lade-Reihenfolge

    Verwendung::

        orch = IntegrationOrchestrator()
        orch.load_category("engines")
        orch.emit("system.ready", source="orchestrator", payload={})
        print(orch.health_report())
    """

    def __init__(
        self,
        registry: Optional[FragmentRegistry] = None,
        mapper: Optional[DependencyMapper] = None,
    ):
        self._registry = registry or get_registry()
        self._mapper = mapper or DependencyMapper()
        self._handles: Dict[str, FragmentHandle] = {}
        self._event_queue: List[OrchestratorEvent] = []
        self._event_lock = threading.Lock()
        self._subscribers: Dict[str, List[Callable]] = {}
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Fragment lifecycle
    # ------------------------------------------------------------------

    def register(self, fragment_id: str) -> Optional[FragmentHandle]:
        """Registriert ein Fragment für das Orchestration-Lifecycle."""
        info = self._registry.get(fragment_id)
        if info is None:
            logger.warning("Fragment not found in registry: %s", fragment_id)
            return None
        if fragment_id in self._handles:
            return self._handles[fragment_id]
        handle = FragmentHandle(info)
        self._handles[fragment_id] = handle
        return handle

    def load(self, fragment_id: str) -> bool:
        """
        Lädt ein Fragment dynamisch.
        Gibt True zurück wenn erfolgreich.
        """
        handle = self._handles.get(fragment_id) or self.register(fragment_id)
        if handle is None:
            return False
        if handle.state == FragmentState.ACTIVE:
            return True

        handle.state = FragmentState.LOADING
        module = self._registry.load_fragment(fragment_id)
        if module is None:
            handle.state = FragmentState.ERROR
            handle.error = f"Could not load module: {fragment_id}"
            logger.error("Failed to load fragment: %s", fragment_id)
            return False

        handle.module = module
        handle.state = FragmentState.ACTIVE
        handle.started_at = datetime.now(timezone.utc).isoformat()
        logger.info("Fragment loaded: %s", fragment_id)
        return True

    def load_category(self, category: str) -> Dict[str, bool]:
        """Lädt alle Fragmente einer Kategorie. Gibt {id: success} zurück."""
        fragments = self._registry.list_by_category(category)
        results = {}
        for frag in fragments:
            results[frag.id] = self.load(frag.id)
        return results

    def load_all(self) -> Dict[str, bool]:
        """Lädt alle registrierten Fragmente."""
        results = {}
        for frag in self._registry.list_all():
            results[frag.id] = self.load(frag.id)
        return results

    def stop(self, fragment_id: str) -> bool:
        """Stoppt ein aktives Fragment."""
        handle = self._handles.get(fragment_id)
        if handle is None:
            return False
        handle.state = FragmentState.STOPPED
        handle.module = None
        logger.info("Fragment stopped: %s", fragment_id)
        return True

    def restart(self, fragment_id: str) -> bool:
        """Stoppt und lädt ein Fragment neu."""
        self.stop(fragment_id)
        frag_info = self._registry.get(fragment_id)
        if frag_info:
            frag_info.loaded_module = None
        return self.load(fragment_id)

    # ------------------------------------------------------------------
    # Event routing
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Registriert einen globalen Event-Handler."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def emit(
        self,
        event_type: str,
        source: str = "orchestrator",
        payload: Optional[Dict] = None,
    ) -> OrchestratorEvent:
        """Sendet ein Event an alle Subscriber und Fragment-Handler."""
        event = OrchestratorEvent(event_type, source, payload or {})
        with self._event_lock:
            self._event_queue.append(event)
        self._dispatch_event(event)
        return event

    def _dispatch_event(self, event: OrchestratorEvent) -> None:
        """Verteilt ein Event an alle Subscriber."""
        handlers = self._subscribers.get(event.event_type, [])
        handlers += self._subscribers.get("*", [])
        for handler in handlers:
            try:
                handler(event)
                event.handled_by.append(getattr(handler, "__name__", str(handler)))
            except Exception as exc:
                logger.warning("Event handler error (%s): %s", event.event_type, exc)

        for handle in self._handles.values():
            if handle.state == FragmentState.ACTIVE:
                h = handle.event_handlers.get(event.event_type)
                if h:
                    try:
                        h(event)
                        event.handled_by.append(handle.fragment_id)
                    except Exception as exc:
                        logger.warning(
                            "Fragment event handler error (%s / %s): %s",
                            handle.fragment_id,
                            event.event_type,
                            exc,
                        )

    # ------------------------------------------------------------------
    # Health monitoring
    # ------------------------------------------------------------------

    def health_report(self) -> Dict:
        """Gibt einen Health-Report aller verwalteten Fragmente zurück."""
        counts: Dict[str, int] = {s.value: 0 for s in FragmentState}
        errors: List[Dict] = []

        for handle in self._handles.values():
            counts[handle.state.value] += 1
            if handle.state == FragmentState.ERROR:
                errors.append({"fragment_id": handle.fragment_id, "error": handle.error})

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_managed": len(self._handles),
            "total_registry": self._registry.total_fragments,
            "state_counts": counts,
            "errors": errors,
            "event_queue_size": len(self._event_queue),
        }

    def active_fragments(self) -> List[FragmentHandle]:
        """Gibt alle aktiven Fragment-Handles zurück."""
        return [h for h in self._handles.values() if h.state == FragmentState.ACTIVE]

    def error_fragments(self) -> List[FragmentHandle]:
        """Gibt alle fehlerhafte Fragment-Handles zurück."""
        return [h for h in self._handles.values() if h.state == FragmentState.ERROR]

    # ------------------------------------------------------------------
    # Dependency-aware loading order
    # ------------------------------------------------------------------

    def load_in_dependency_order(self, fragment_ids: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Lädt Fragmente in einer Reihenfolge, die Dependency-Konflikte
        minimiert (einfache topologische Sortierung).
        """
        if fragment_ids is None:
            fragment_ids = [f.id for f in self._registry.list_all()]

        self._mapper.analyse_all()
        dep_graph = self._mapper.dependency_graph()

        # Topological sort (Kahn's algorithm simplified)
        in_degree: Dict[str, int] = {fid: 0 for fid in fragment_ids}
        # We only count deps that are themselves in the load set
        fid_set = set(fragment_ids)
        adjacency: Dict[str, Set[str]] = {fid: set() for fid in fragment_ids}

        for fid in fragment_ids:
            deps = dep_graph.get(fid, [])
            for dep in deps:
                # Map dep module name to fragment_id heuristically
                dep_fid = dep.replace(".", "_")
                for candidate in fid_set:
                    if candidate.endswith(dep_fid) or candidate.endswith(dep):
                        if candidate != fid:
                            adjacency[candidate].add(fid)
                            in_degree[fid] += 1

        queue = [fid for fid, deg in in_degree.items() if deg == 0]
        order: List[str] = []
        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adjacency.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Any remaining (cycle) – append as-is
        remaining = [fid for fid in fragment_ids if fid not in order]
        order.extend(remaining)

        results = {}
        for fid in order:
            results[fid] = self.load(fid)
        return results

    # ------------------------------------------------------------------
    # Background worker
    # ------------------------------------------------------------------

    def start_background_monitor(self, interval_seconds: int = 60) -> None:
        """Startet einen Hintergrund-Thread für periodische Health-Checks."""
        if self._running:
            return
        self._running = True

        def _run() -> None:
            while self._running:
                report = self.health_report()
                if report["errors"]:
                    for err in report["errors"]:
                        logger.warning(
                            "Fragment error detected: %s – %s",
                            err["fragment_id"],
                            err["error"],
                        )
                time.sleep(interval_seconds)

        self._worker_thread = threading.Thread(target=_run, daemon=True, name="orchestrator-monitor")
        self._worker_thread.start()
        logger.info("Background monitor started (interval=%ds)", interval_seconds)

    def stop_background_monitor(self) -> None:
        """Stoppt den Hintergrund-Monitor."""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "IntegrationOrchestrator":
        return self

    def __exit__(self, *args: Any) -> None:
        self.stop_background_monitor()

    def __repr__(self) -> str:
        return (
            f"<IntegrationOrchestrator "
            f"managed={len(self._handles)} "
            f"active={len(self.active_fragments())}>"
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_orchestrator: Optional[IntegrationOrchestrator] = None


def get_orchestrator() -> IntegrationOrchestrator:
    """Gibt die globale IntegrationOrchestrator-Instanz zurück (lazy-init)."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IntegrationOrchestrator()
    return _orchestrator


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    print("IntegrationOrchestrator – starte …")
    orch = get_orchestrator()

    # Zeige Registry-Übersicht
    print(f"\nRegistry: {orch._registry}")
    stats = orch._registry.statistics()
    print(f"Fragmente: {stats['total_fragments']}, Kategorien: {list(stats['categories'].keys())}")

    # Lade eine Beispiel-Kategorie
    print("\nLade Kategorie 'core' …")
    results = orch.load_category("core")
    ok = sum(1 for v in results.values() if v)
    fail = sum(1 for v in results.values() if not v)
    print(f"  Geladen: {ok}, Fehler: {fail}")

    print("\nHealth Report:")
    report = orch.health_report()
    for k, v in report.items():
        print(f"  {k}: {v}")
