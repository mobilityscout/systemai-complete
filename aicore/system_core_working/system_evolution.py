import os, json

BASE = "/root/aicore"
BRAIN = BASE + "/brain.json"
GRAPH = BASE + "/system_graph.json"
REPORT = BASE + "/principle_report.json"

def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def detect_duplicates(brain):
    seen = {}
    duplicates = []

    for path in brain:
        name = os.path.basename(path)

        if name in seen:
            duplicates.append(path)
        else:
            seen[name] = path

    return duplicates

def detect_garbage(brain):
    garbage = []

    for path, data in brain.items():
        p = path.lower()

        if "quarantine" in p or "backup" in p:
            garbage.append(path)

        elif data.get("decision") == "ignore":
            garbage.append(path)

    return garbage

def propose_structure(graph):

    structure = {}

    for name, data in graph.items():

        role = data.get("role", "unknown")

        if role == "central_hub":
            target = "core"
        elif role == "core_module":
            target = "engine"
        elif role == "support_module":
            target = "modules"
        else:
            target = "isolated"

        structure.setdefault(target, []).append(data["path"])

    return structure

def run():

    print("[EVOLVE] analyzing system...")

    brain = load(BRAIN)
    graph = load(GRAPH)

    if not brain or not graph:
        print("[EVOLVE] missing data")
        return

    duplicates = detect_duplicates(brain)
    garbage = detect_garbage(brain)
    structure = propose_structure(graph)

    report = {
        "duplicates": duplicates,
        "garbage_candidates": garbage,
        "proposed_structure": structure
    }

    with open(REPORT, "w") as f:
        json.dump(report, f, indent=2)

    print("[EVOLVE] report created")

    print("[EVOLVE] duplicates:", len(duplicates))
    print("[EVOLVE] garbage:", len(garbage))

    print("[EVOLVE] structure:")
    for k in structure:
        print(" -", k, len(structure[k]))

if __name__ == "__main__":
    run()
