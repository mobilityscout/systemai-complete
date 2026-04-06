# SystemAI Fragment Architecture

## Übersicht

Dieses Dokument beschreibt die zentrale Integration Registry für alle **227 Python-Fragmente** des SystemAI-Projekts.

| Metrik | Wert |
|---|---|
| Fragmente gesamt | 227 |
| Zeilen gesamt | ~13.000 |
| Kategorien | 9 |
| Größtes Modul | `ai_developer_brain.py` (528 Zeilen) |

---

## Verzeichnisstruktur

```
aicore/
├── fragment_registry.py        # Zentrale Registry für alle Module
├── dependency_mapper.py        # Automatisches Import/Dependency-Mapping
├── integration_orchestrator.py # Koordiniert Fragment-Zusammenspiel
├── FRAGMENT_MANIFEST.json      # Vollständiges Verzeichnis aller Module
│
├── # Top-Level Fragmente (engines, managers, intelligence …)
├── ai_developer_brain.py
├── enterprise_control_plane.py
├── intelligent_conversation_engine.py
├── …
│
├── core/                       # Master-Brain & Chat-Assistant
│   ├── master_brain.py
│   └── chat_assistant.py
│
├── shared/                     # Shared Services
│   ├── auth_service.py
│   └── cache_layer.py
│
├── internal/                   # Interne Infrastruktur
│   └── infra_manager.py
│
├── external/                   # Externe Integrationen
│   └── app_builder.py
│
├── workspace/                  # Workspace-Management
│   ├── api.py
│   ├── billing.py
│   ├── customer.py
│   ├── handler.py
│   ├── loader.py
│   ├── registry.py
│   └── router.py
│
└── system_core_working/        # System-Core (Legacy + Working-Copy)
    ├── *.py                    # ~150 Module
    └── modules/aicore_backup/  # Backup-Kopien
```

---

## Kategorien

| Kategorie | Beschreibung | Typische Module |
|---|---|---|
| `engines` | Verarbeitungs- und Analyse-Engines | `dependency_engine`, `evolution_engine`, `memory_engine` |
| `healers` | Self-Healing, Repair, Guard-Logik | `self_healer`, `auto_repair`, `core_guard`, `immune_daemon` |
| `managers` | Verwaltungs- und Koordinations-Schichten | `ai_manager`, `multi_project_manager`, `tenant_manager` |
| `intelligence` | Brain, Reasoning, Kognition | `ai_developer_brain`, `intelligent_conversation_engine`, `principle_brain` |
| `memory` | Speicher, Wissen, Lernen | `memory_engine`, `knowledge_engine`, `learning_engine` |
| `workers` | Ausführungs- und Worker-Schichten | `worker_pool`, `worker_builder`, `executor_engine` |
| `core` | System-Core, Runtime, State | `system_loop`, `state_manager`, `system_runtime` |
| `api` | API, Server, Gateway | `server`, `unified_gateway`, `projects_api` |
| `misc` | Alle weiteren Module | diverse |

---

## Neue Dateien – Kurzbeschreibung

### `fragment_registry.py`

Zentrale Registry, die das `FRAGMENT_MANIFEST.json` einliest und
eine einheitliche Query-API bereitstellt:

```python
from aicore.fragment_registry import get_registry

registry = get_registry()

# Alle Fragmente einer Kategorie
engines = registry.list_by_category("engines")

# Suche nach Stichwort
results = registry.search("self heal")

# Statistiken
print(registry.statistics())
```

### `dependency_mapper.py`

Analysiert alle `.py`-Dateien per `ast`-Parser und erstellt ein
vollständiges Dependency-Mapping:

```python
from aicore.dependency_mapper import DependencyMapper

mapper = DependencyMapper()
mapper.analyse_all()

# Welche Fragmente nutzen 'flask'?
users = mapper.fragments_using("flask")

# Vollständiger Dependency-Graph
graph = mapper.dependency_graph()

# Export als JSON
mapper.export_json()

# Manifest aktualisieren
mapper.update_manifest()
```

### `integration_orchestrator.py`

Koordiniert Lifecycle und Event-Routing aller Fragmente:

```python
from aicore.integration_orchestrator import get_orchestrator

orch = get_orchestrator()

# Kategorie laden
orch.load_category("engines")

# Event senden
orch.emit("system.ready", source="main", payload={"version": "1.0"})

# Health-Report
print(orch.health_report())

# Dependency-gesteuertes Laden
orch.load_in_dependency_order()
```

### `FRAGMENT_MANIFEST.json`

Maschinenlesbares Verzeichnis aller 227 Fragmente.
Enthält je Fragment:

- `id`, `name`, `file`, `path`, `subdirectory`, `category`
- `line_count`, `imports`, `classes`, `functions`, `docstring`

Wird automatisch durch `dependency_mapper.py --update-manifest` aktualisiert.

---

## CLI-Verwendung

```bash
# Registry-Übersicht
python3 aicore/fragment_registry.py

# Suche im Manifest
python3 aicore/fragment_registry.py "self heal"

# Dependency-Analyse
python3 aicore/dependency_mapper.py

# Dependency-Map exportieren
python3 aicore/dependency_mapper.py --export

# Manifest aktualisieren
python3 aicore/dependency_mapper.py --update-manifest

# Orchestrator-Demo
python3 aicore/integration_orchestrator.py
```

---

## Top-10 Module nach Zeilenzahl

| # | Datei | Zeilen |
|---|---|---|
| 1 | `ai_developer_brain.py` | 528 |
| 2 | `enterprise_control_plane.py` | 501 |
| 3 | `intelligent_conversation_engine.py` | 476 |
| 4 | `developer_chat_ui.py` | 321 |
| 5 | `smart_chat_engine.py` | 313 |
| 6 | `principle_brain.py` | 303 |
| 7 | `core/chat_assistant.py` | 275 |
| 8 | `developer_chat_backend.py` | 234 |
| 9 | `system_core_working/state_core_engine.py` | 206 |
| 10 | `system_core_working/ai_manager.py` | 191 |

---

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────┐
│                IntegrationOrchestrator              │
│  ┌───────────────────┐   ┌────────────────────────┐ │
│  │  FragmentRegistry  │   │   DependencyMapper     │ │
│  │  (227 Fragmente)   │   │  (Import-Graph)        │ │
│  └───────────────────┘   └────────────────────────┘ │
│           │                          │               │
│           └──────────┬───────────────┘               │
│                      ▼                               │
│              FRAGMENT_MANIFEST.json                  │
└─────────────────────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
    [engines]   [healers]   [intelligence]  …
```
