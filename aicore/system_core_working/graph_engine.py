import os, json

MEMORY = "/root/aicore/memory.json"
GRAPH  = "/root/aicore/graph.json"

def load(path, default):
    try:
        return json.load(open(path))
    except:
        return default

def save(path, data):
    json.dump(data, open(path,"w"))

def extract_relations(file, data):

    relations = []

    # 🔗 IMPORT RELATIONEN
    if "import " in data.get("summary",""):
        relations.append({"type":"imports", "target":"unknown"})

    # 🔗 FUNKTIONSLOGIK
    if data.get("functions",0) > 0:
        relations.append({"type":"defines_logic"})

    # 🔗 KLASSEN = STRUKTUR
    if data.get("classes",0) > 0:
        relations.append({"type":"defines_structure"})

    return relations

def run():

    mem = load(MEMORY, {})
    graph = {"nodes":{}, "edges":[]}

    for path, info in mem.get("files", {}).items():

        node = {
            "file": path,
            "module": info["module"],
            "functions": info["data"]["functions"],
            "classes": info["data"]["classes"]
        }

        graph["nodes"][path] = node

        relations = extract_relations(path, info["data"])

        for r in relations:
            graph["edges"].append({
                "from": path,
                "type": r["type"]
            })

    save(GRAPH, graph)

    return {
        "nodes": len(graph["nodes"]),
        "edges": len(graph["edges"])
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
