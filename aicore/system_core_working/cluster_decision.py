import json, os

CLUSTERS = "/root/aicore/system_clusters.json"
GRAPH = "/root/aicore/system_graph.json"

def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def cluster_connections(graph, files):
    score = 0
    for f in files:
        node = graph.get(f, {})
        score += len(node.get("connected_to", []))
    return score

def evaluate_cluster(cluster, graph):

    files = cluster["files"]
    size = cluster["size"]
    topic = cluster["topic"]

    conn = cluster_connections(graph, files)

    # LOGIK
    if size > 20 and conn > 50:
        status = "core_system"
        action = "keep + refine"

    elif size > 5 and conn > 10:
        status = "important_module"
        action = "analyze deeper"

    elif size <= 2 and conn == 0:
        status = "fragment"
        action = "observe"

    elif "quarantine" in topic or "backup" in topic:
        status = "legacy_cluster"
        action = "archive"

    else:
        status = "unclear"
        action = "investigate"

    return {
        "topic": topic,
        "size": size,
        "connections": conn,
        "status": status,
        "action": action
    }

def run():

    print("\n[CLUSTER DECISION]\n")

    clusters = load(CLUSTERS)
    graph = load(GRAPH)

    results = []

    for c in clusters:
        r = evaluate_cluster(c, graph)
        results.append(r)

        print("System:", r["topic"])
        print(" Size:", r["size"])
        print(" Connections:", r["connections"])
        print(" Status:", r["status"])
        print(" Action:", r["action"])
        print("")

if __name__ == "__main__":
    run()
