import json, os

GRAPH = "/root/aicore/system_graph.json"
OUT = "/root/aicore/system_clusters.json"

def load():
    if not os.path.exists(GRAPH):
        return {}
    with open(GRAPH, "r") as f:
        return json.load(f)

def build_clusters(graph):

    clusters = []

    visited = set()

    for node in graph:

        if node in visited:
            continue

        stack = [node]
        group = []

        while stack:
            n = stack.pop()
            if n in visited:
                continue

            visited.add(n)
            group.append(n)

            for c in graph[n].get("connected_to", []):
                if c not in visited:
                    stack.append(c)

        clusters.append(group)

    return clusters

def detect_topic(files):

    words = []

    for f in files:
        name = f.lower().replace(".py","").split("_")
        words.extend(name)

    common = {}
    for w in words:
        common[w] = common.get(w, 0) + 1

    topic = sorted(common, key=common.get, reverse=True)[:2]

    return "_".join(topic)

def run():

    print("[CLUSTER] building systems...")

    graph = load()

    if not graph:
        print("[CLUSTER] no graph")
        return

    clusters = build_clusters(graph)

    result = []

    for c in clusters:

        topic = detect_topic(c)

        result.append({
            "topic": topic,
            "size": len(c),
            "files": c
        })

    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

    print("[CLUSTER] systems:", len(result))

    for r in result[:10]:
        print(" -", r["topic"], "(", r["size"], ")")

if __name__ == "__main__":
    run()
