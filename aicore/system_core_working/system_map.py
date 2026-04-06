import os, json, re

BASE = "/root/aicore"
BRAIN = BASE + "/brain.json"
GRAPH = BASE + "/system_graph.json"

def load_brain():
    if not os.path.exists(BRAIN):
        return {}
    with open(BRAIN, "r") as f:
        return json.load(f)

def extract_imports(path):
    try:
        with open(path, "r", errors="ignore") as f:
            content = f.read()
    except:
        return []

    imports = re.findall(r'(?:from|import)\s+([\w\.]+)', content)
    return list(set(imports))

def build_graph(brain):

    graph = {}

    for path in brain:

        name = os.path.basename(path)

        imports = extract_imports(path)

        graph[name] = {
            "path": path,
            "imports": imports,
            "connected_to": []
        }

    # Verbindungen herstellen
    for name, data in graph.items():

        for imp in data["imports"]:
            for target in graph:
                if imp in target:
                    data["connected_to"].append(target)

    return graph

def detect_roles(graph):

    roles = {}

    for name, data in graph.items():

        conns = len(data["connected_to"])

        if conns > 10:
            role = "central_hub"
        elif conns > 5:
            role = "core_module"
        elif conns > 1:
            role = "support_module"
        else:
            role = "isolated"

        roles[name] = role

    return roles

def run():

    print("[MAP] building system graph...")

    brain = load_brain()

    if not brain:
        print("[MAP] no brain")
        return

    graph = build_graph(brain)
    roles = detect_roles(graph)

    # Rollen ins Graph schreiben
    for k in graph:
        graph[k]["role"] = roles.get(k, "unknown")

    with open(GRAPH, "w") as f:
        json.dump(graph, f, indent=2)

    print("[MAP] nodes:", len(graph))

    # wichtigste Module anzeigen
    hubs = [k for k,v in graph.items() if v["role"] == "central_hub"]

    print("[MAP] central modules:")
    for h in hubs[:10]:
        print(" -", h)

if __name__ == "__main__":
    run()
