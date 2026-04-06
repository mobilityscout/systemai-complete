#!/usr/bin/env python3
"""
FRAGMENT REGISTRY
Zentrale Registry für alle 227 Python-Fragmente des SystemAI.
Verwaltet Metadaten, Status und Zugriff auf alle Module.
"""

import json
import os
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


MANIFEST_PATH = Path(__file__).parent / "FRAGMENT_MANIFEST.json"
AICORE_BASE = Path(__file__).parent


class FragmentInfo:
    """Metadaten eines einzelnen Fragments."""

    def __init__(self, data: Dict):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.file: str = data.get("file", "")
        self.path: str = data.get("path", "")
        self.subdirectory: str = data.get("subdirectory", ".")
        self.category: str = data.get("category", "misc")
        self.line_count: int = data.get("line_count", 0)
        self.imports: List[str] = data.get("imports", [])
        self.classes: List[str] = data.get("classes", [])
        self.functions: List[str] = data.get("functions", [])
        self.docstring: str = data.get("docstring", "")
        self.status: str = "registered"
        self.loaded_module: Optional[Any] = None
        self.registered_at: str = datetime.now(timezone.utc).isoformat()

    @property
    def absolute_path(self) -> Path:
        return AICORE_BASE / self.path

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "file": self.file,
            "path": self.path,
            "subdirectory": self.subdirectory,
            "category": self.category,
            "line_count": self.line_count,
            "imports": self.imports,
            "classes": self.classes,
            "functions": self.functions,
            "docstring": self.docstring,
            "status": self.status,
            "registered_at": self.registered_at,
        }

    def __repr__(self) -> str:
        return f"<FragmentInfo id={self.id!r} category={self.category!r} lines={self.line_count}>"


class FragmentRegistry:
    """
    Zentrale Registry für alle 227 Python-Fragmente.

    Lädt das FRAGMENT_MANIFEST.json und stellt Methoden
    bereit, um Fragmente nach ID, Name, Kategorie oder
    Subdirectory abzufragen.
    """

    def __init__(self, manifest_path: Optional[Path] = None):
        self._manifest_path = manifest_path or MANIFEST_PATH
        self._fragments: Dict[str, FragmentInfo] = {}
        self._manifest_meta: Dict = {}
        self._load_manifest()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_manifest(self) -> None:
        """Lädt alle Fragmente aus FRAGMENT_MANIFEST.json."""
        if not self._manifest_path.exists():
            raise FileNotFoundError(
                f"Manifest not found: {self._manifest_path}. "
                "Run the dependency_mapper to regenerate it."
            )
        with open(self._manifest_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        self._manifest_meta = data.get("statistics", {})
        for fragment_data in data.get("fragments", []):
            info = FragmentInfo(fragment_data)
            self._fragments[info.id] = info

    def reload(self) -> None:
        """Lädt das Manifest neu (z.B. nach einer Änderung)."""
        self._fragments.clear()
        self._load_manifest()

    # ------------------------------------------------------------------
    # Query API
    # ------------------------------------------------------------------

    def get(self, fragment_id: str) -> Optional[FragmentInfo]:
        """Gibt ein Fragment nach seiner ID zurück."""
        return self._fragments.get(fragment_id)

    def get_by_name(self, name: str) -> Optional[FragmentInfo]:
        """Gibt das erste Fragment zurück, dessen `name` übereinstimmt."""
        for frag in self._fragments.values():
            if frag.name == name:
                return frag
        return None

    def get_by_file(self, filename: str) -> Optional[FragmentInfo]:
        """Gibt das Fragment zurück, das `filename` entspricht (z.B. 'brain.py')."""
        for frag in self._fragments.values():
            if frag.file == filename:
                return frag
        return None

    def list_all(self) -> List[FragmentInfo]:
        """Gibt alle registrierten Fragmente zurück."""
        return list(self._fragments.values())

    def list_by_category(self, category: str) -> List[FragmentInfo]:
        """Filtert Fragmente nach Kategorie."""
        return [f for f in self._fragments.values() if f.category == category]

    def list_by_subdirectory(self, subdirectory: str) -> List[FragmentInfo]:
        """Filtert Fragmente nach Subdirectory."""
        return [f for f in self._fragments.values() if f.subdirectory == subdirectory]

    def search(self, query: str) -> List[FragmentInfo]:
        """Einfache Freitext-Suche über Name, Docstring und Klassen."""
        q = query.lower()
        results = []
        for frag in self._fragments.values():
            haystack = " ".join([
                frag.name,
                frag.docstring,
                " ".join(frag.classes),
                " ".join(frag.functions),
            ]).lower()
            if q in haystack:
                results.append(frag)
        return results

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    @property
    def total_fragments(self) -> int:
        return len(self._fragments)

    @property
    def categories(self) -> List[str]:
        return sorted(set(f.category for f in self._fragments.values()))

    def statistics(self) -> Dict:
        """Gibt Statistiken über alle registrierten Fragmente zurück."""
        cat_counts: Dict[str, int] = {}
        total_lines = 0
        for frag in self._fragments.values():
            cat_counts[frag.category] = cat_counts.get(frag.category, 0) + 1
            total_lines += frag.line_count

        top_modules = sorted(
            self._fragments.values(), key=lambda f: f.line_count, reverse=True
        )[:10]

        return {
            "total_fragments": self.total_fragments,
            "total_lines": total_lines,
            "categories": cat_counts,
            "top_modules": [
                {"name": f.file, "lines": f.line_count} for f in top_modules
            ],
        }

    # ------------------------------------------------------------------
    # Dynamic loading
    # ------------------------------------------------------------------

    def load_fragment(self, fragment_id: str) -> Optional[Any]:
        """
        Lädt ein Fragment dynamisch als Python-Modul.
        Gibt das Modul-Objekt zurück oder None bei Fehler.
        """
        frag = self.get(fragment_id)
        if frag is None:
            return None
        if frag.loaded_module is not None:
            return frag.loaded_module

        try:
            spec = importlib.util.spec_from_file_location(frag.name, str(frag.absolute_path))
            if spec is None or spec.loader is None:
                frag.status = "load_error"
                return None
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]
            frag.loaded_module = module
            frag.status = "loaded"
            return module
        except Exception as exc:
            frag.status = f"load_error: {exc}"
            return None

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._fragments)

    def __contains__(self, fragment_id: str) -> bool:
        return fragment_id in self._fragments

    def __repr__(self) -> str:
        return f"<FragmentRegistry fragments={self.total_fragments} categories={len(self.categories)}>"


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_registry: Optional[FragmentRegistry] = None


def get_registry() -> FragmentRegistry:
    """Gibt die globale FragmentRegistry-Instanz zurück (lazy-init)."""
    global _registry
    if _registry is None:
        _registry = FragmentRegistry()
    return _registry


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    registry = get_registry()
    print(f"FragmentRegistry geladen: {registry}")
    print()

    stats = registry.statistics()
    print("=== Statistiken ===")
    print(f"  Fragmente gesamt : {stats['total_fragments']}")
    print(f"  Zeilen gesamt    : {stats['total_lines']}")
    print(f"  Kategorien       : {list(stats['categories'].keys())}")
    print()
    print("  Top 5 Module:")
    for m in stats["top_modules"][:5]:
        print(f"    {m['name']:50s} {m['lines']} Zeilen")
    print()

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        results = registry.search(query)
        print(f"=== Suche: '{query}' → {len(results)} Treffer ===")
        for f in results[:10]:
            print(f"  {f.path}")
