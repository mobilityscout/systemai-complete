#!/usr/bin/env python3
"""
DEPENDENCY MAPPER
Analysiert automatisch alle Imports und erstellt ein vollständiges
Dependency-Graph-Mapping für alle 227 Python-Fragmente.
"""

import ast
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timezone


AICORE_BASE = Path(__file__).parent
MANIFEST_PATH = AICORE_BASE / "FRAGMENT_MANIFEST.json"
_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Standard library modules (partial list for filtering)
_STDLIB_TOP = {
    "abc", "ast", "asyncio", "base64", "collections", "concurrent",
    "contextlib", "copy", "csv", "datetime", "decimal", "email",
    "enum", "functools", "glob", "hashlib", "html", "http", "importlib",
    "inspect", "io", "itertools", "json", "logging", "math", "multiprocessing",
    "operator", "os", "pathlib", "pickle", "platform", "pprint", "queue",
    "random", "re", "shutil", "signal", "socket", "sqlite3", "ssl",
    "stat", "string", "subprocess", "sys", "tempfile", "threading",
    "time", "traceback", "typing", "unittest", "urllib", "uuid",
    "warnings", "weakref", "xml", "zipfile",
}


def _top_level(module_name: str) -> str:
    """Gibt den Top-Level-Namespace eines Modulnamens zurück."""
    return module_name.split(".")[0] if module_name else ""


def _classify_import(module_name: str) -> str:
    """Klassifiziert einen Import als 'stdlib', 'third_party' oder 'internal'."""
    top = _top_level(module_name)
    if top in _STDLIB_TOP:
        return "stdlib"
    # Internal modules – bekannte Pfad-Präfixe dieses Projekts
    internal_prefixes = {
        "aicore", "workspace", "core", "shared", "internal",
        "external", "system_core_working",
    }
    if top in internal_prefixes:
        return "internal"
    return "third_party"


class ImportRecord:
    """Repräsentiert einen einzelnen Import in einer Quelldatei."""

    def __init__(
        self,
        module: str,
        names: List[str],
        is_from: bool,
        line: int,
        import_type: str,
    ):
        self.module = module
        self.names = names
        self.is_from = is_from
        self.line = line
        self.import_type = import_type  # stdlib | third_party | internal

    def to_dict(self) -> Dict:
        return {
            "module": self.module,
            "names": self.names,
            "is_from": self.is_from,
            "line": self.line,
            "import_type": self.import_type,
        }


class FragmentDependencies:
    """Dependency-Informationen für ein einzelnes Fragment."""

    def __init__(self, fragment_id: str, path: str):
        self.fragment_id = fragment_id
        self.path = path
        self.imports: List[ImportRecord] = []
        self.parse_error: Optional[str] = None

    # Abgeleitete Sichten
    @property
    def stdlib_deps(self) -> List[str]:
        return sorted({r.module for r in self.imports if r.import_type == "stdlib"})

    @property
    def third_party_deps(self) -> List[str]:
        return sorted({r.module for r in self.imports if r.import_type == "third_party"})

    @property
    def internal_deps(self) -> List[str]:
        return sorted({r.module for r in self.imports if r.import_type == "internal"})

    @property
    def all_deps(self) -> List[str]:
        return sorted({r.module for r in self.imports})

    def to_dict(self) -> Dict:
        return {
            "fragment_id": self.fragment_id,
            "path": self.path,
            "parse_error": self.parse_error,
            "stdlib_deps": self.stdlib_deps,
            "third_party_deps": self.third_party_deps,
            "internal_deps": self.internal_deps,
            "imports": [r.to_dict() for r in self.imports],
        }


class DependencyMapper:
    """
    Analysiert alle Python-Fragmente und baut ein vollständiges
    Dependency-Mapping auf.

    Verwendung::

        mapper = DependencyMapper()
        mapper.analyse_all()
        graph = mapper.dependency_graph()
        print(mapper.summary())
    """

    def __init__(self, base_path: Optional[Path] = None):
        self._base = base_path or AICORE_BASE
        self._deps: Dict[str, FragmentDependencies] = {}
        self._analysed = False

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyse_all(self) -> None:
        """Analysiert alle .py-Dateien unterhalb von base_path."""
        self._deps.clear()
        for root, dirs, files in os.walk(self._base):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fname in sorted(files):
                if not fname.endswith(".py"):
                    continue
                full = Path(root) / fname
                rel = full.relative_to(self._base)
                fragment_id = str(rel).replace(os.sep, ".")[:-3]
                self._analyse_file(fragment_id, str(rel), full)
        self._analysed = True

    def _analyse_file(
        self, fragment_id: str, rel_path: str, full_path: Path
    ) -> None:
        fd = FragmentDependencies(fragment_id, rel_path)
        try:
            source = full_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(full_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        itype = _classify_import(alias.name)
                        fd.imports.append(
                            ImportRecord(alias.name, [], False, node.lineno, itype)
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    names = [a.name for a in node.names]
                    itype = _classify_import(module)
                    fd.imports.append(
                        ImportRecord(module, names, True, node.lineno, itype)
                    )
        except SyntaxError as exc:
            fd.parse_error = str(exc)
        except Exception as exc:
            fd.parse_error = f"unexpected error: {exc}"
        self._deps[fragment_id] = fd

    # ------------------------------------------------------------------
    # Graph & Query
    # ------------------------------------------------------------------

    def dependency_graph(self) -> Dict[str, List[str]]:
        """
        Gibt einen einfachen Dependency-Graphen zurück:
        { fragment_id: [dep1, dep2, ...] }
        """
        self._ensure_analysed()
        return {fid: fd.all_deps for fid, fd in self._deps.items()}

    def reverse_graph(self) -> Dict[str, List[str]]:
        """
        Gibt den umgekehrten Graphen zurück:
        { module: [fragment_id der Nutzer, ...] }
        """
        self._ensure_analysed()
        rev: Dict[str, List[str]] = defaultdict(list)
        for fid, fd in self._deps.items():
            for dep in fd.all_deps:
                rev[dep].append(fid)
        return dict(rev)

    def get(self, fragment_id: str) -> Optional[FragmentDependencies]:
        self._ensure_analysed()
        return self._deps.get(fragment_id)

    def fragments_using(self, module_name: str) -> List[str]:
        """Gibt alle Fragment-IDs zurück, die `module_name` importieren."""
        self._ensure_analysed()
        return [
            fid
            for fid, fd in self._deps.items()
            if module_name in fd.all_deps
        ]

    def third_party_packages(self) -> Set[str]:
        """Alle Third-Party-Pakete, die im Projekt verwendet werden."""
        self._ensure_analysed()
        pkgs: Set[str] = set()
        for fd in self._deps.values():
            for dep in fd.third_party_deps:
                pkgs.add(_top_level(dep))
        return pkgs

    # ------------------------------------------------------------------
    # Summary & Export
    # ------------------------------------------------------------------

    def summary(self) -> Dict:
        """Gibt eine Zusammenfassung der Analyse zurück."""
        self._ensure_analysed()
        errors = [fid for fid, fd in self._deps.items() if fd.parse_error]
        all_third = self.third_party_packages()

        dep_counts = [(fid, len(fd.all_deps)) for fid, fd in self._deps.items()]
        top_deps = sorted(dep_counts, key=lambda x: x[1], reverse=True)[:10]

        return {
            "analysed_fragments": len(self._deps),
            "parse_errors": len(errors),
            "error_fragments": errors,
            "unique_third_party_packages": sorted(all_third),
            "top_fragments_by_deps": [
                {"fragment": fid, "dep_count": cnt} for fid, cnt in top_deps
            ],
        }

    def export_json(self, output_path: Optional[Path] = None) -> Path:
        """Exportiert das vollständige Mapping als JSON-Datei."""
        self._ensure_analysed()
        out = output_path or (self._base / "dependency_map.json")
        payload = {
            "generated_at": datetime.now(timezone.utc).strftime(_TIMESTAMP_FORMAT),
            "base_path": str(self._base),
            "summary": self.summary(),
            "fragments": {
                fid: fd.to_dict() for fid, fd in self._deps.items()
            },
        }
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        return out

    # ------------------------------------------------------------------
    # Manifest update
    # ------------------------------------------------------------------

    def update_manifest(self) -> None:
        """
        Aktualisiert FRAGMENT_MANIFEST.json mit frischen Statistiken.
        Analysiert alle Dateien neu und schreibt das Manifest.
        """
        self._ensure_analysed()
        fragments = []
        for root, dirs, files in os.walk(self._base):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for fname in sorted(files):
                if not fname.endswith(".py"):
                    continue
                full = Path(root) / fname
                rel = str(full.relative_to(self._base)).replace(os.sep, "/")
                fid = rel[:-3].replace("/", ".")

                fd = self._deps.get(fid)
                imports_list = [r.module for r in fd.imports] if fd else []

                # Count lines
                try:
                    lines = full.read_text(encoding="utf-8", errors="ignore").splitlines()
                    lc = len(lines)
                except Exception:
                    lc = 0

                # Extract classes / functions via AST
                classes: List[str] = []
                functions: List[str] = []
                docstring = ""
                try:
                    tree = ast.parse(
                        full.read_text(encoding="utf-8", errors="ignore")
                    )
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.col_offset == 0:
                            classes.append(node.name)
                        elif (
                            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and node.col_offset == 0
                        ):
                            functions.append(node.name)
                    ds = ast.get_docstring(tree)
                    if ds:
                        docstring = ds[:300]
                except Exception:
                    pass

                name = fname[:-3]
                n = name.lower()
                category = "misc"
                if "engine" in n:
                    category = "engines"
                elif any(x in n for x in ["heal", "repair", "immune", "guard", "safe"]):
                    category = "healers"
                elif "manager" in n:
                    category = "managers"
                elif any(x in n for x in ["brain", "intelligence", "cognit", "reason", "principle"]):
                    category = "intelligence"
                elif any(x in n for x in ["memory", "knowledge", "learning"]):
                    category = "memory"
                elif any(x in n for x in ["worker", "executor", "pool"]):
                    category = "workers"
                elif any(x in n for x in ["system", "core", "runtime"]):
                    category = "core"
                elif any(x in n for x in ["api", "server", "gateway", "interface"]):
                    category = "api"

                parts = rel.split("/")
                subdir = parts[0] if len(parts) > 1 else "."

                fragments.append({
                    "id": fid,
                    "name": name,
                    "file": fname,
                    "path": rel,
                    "subdirectory": subdir,
                    "category": category,
                    "line_count": lc,
                    "imports": sorted(list(set(imports_list))),
                    "classes": classes,
                    "functions": functions,
                    "docstring": docstring,
                })

        total_lines = sum(f["line_count"] for f in fragments)
        cat_counts: Dict[str, int] = {}
        for f in fragments:
            cat_counts[f["category"]] = cat_counts.get(f["category"], 0) + 1

        manifest = {
            "manifest_version": "1.0.0",
            "generated_at": datetime.now(timezone.utc).strftime(_TIMESTAMP_FORMAT),
            "repository": "mobilityscout/systemai-complete",
            "base_path": "aicore/",
            "statistics": {
                "total_fragments": len(fragments),
                "total_lines": total_lines,
                "total_categories": len(cat_counts),
                "categories": cat_counts,
                "top_modules": [
                    {"name": f["file"], "lines": f["line_count"]}
                    for f in sorted(fragments, key=lambda x: x["line_count"], reverse=True)[:10]
                ],
            },
            "fragments": fragments,
        }
        with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_analysed(self) -> None:
        if not self._analysed:
            self.analyse_all()

    def __repr__(self) -> str:
        status = "analysed" if self._analysed else "not analysed"
        return f"<DependencyMapper base={self._base} status={status}>"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    print("DependencyMapper – analysiere alle Fragmente …")
    mapper = DependencyMapper()
    mapper.analyse_all()

    summary = mapper.summary()
    print(f"\n=== Dependency-Analyse ===")
    print(f"  Fragmente analysiert : {summary['analysed_fragments']}")
    print(f"  Parse-Fehler         : {summary['parse_errors']}")
    print(f"  Third-Party-Pakete   : {', '.join(summary['unique_third_party_packages'][:15])}")
    print()
    print("  Top 5 Fragmente (meiste Deps):")
    for entry in summary["top_fragments_by_deps"][:5]:
        print(f"    {entry['fragment']:60s} {entry['dep_count']} Deps")

    if "--export" in sys.argv:
        out = mapper.export_json()
        print(f"\nExportiert nach: {out}")

    if "--update-manifest" in sys.argv:
        mapper.update_manifest()
        print(f"\nManifest aktualisiert: {MANIFEST_PATH}")
