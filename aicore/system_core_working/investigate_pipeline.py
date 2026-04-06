import os, json, re

CLUSTERS = "/root/aicore/system_clusters.json"
GRAPH = "/root/aicore/system_graph.json"
OUT = "/root/aicore/investigate_report.json"

def load(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read()
    except:
        return ""

def extract_structure(content):
    funcs = re.findall(r'def\s+(\w+)', content)
    classes = re.findall(r'class\s+(\w+)', content)
    return funcs, classes

def detect_purpose(content):

    c = content.lower()

    purpose = []

    if "request" in c or "api" in c:
        purpose.append("api/service")

    if "state" in c:
        purpose.append("state_management")

    if "execute" in c or "run" in c:
        purpose.append("execution")

    if "learn" in c or "model" in c:
        purpose.append("learning")

    if "generate" in c:
        purpose.append("generation")

    return list(set(purpose))

def describe(path, funcs, classes, purpose):

    desc = []

    desc.append(f"Datei: {os.path.basename(path)}")

    if classes:
        desc.append(f"Definiert Klassen: {', '.join(classes[:3])}")

    if funcs:
        desc.append(f"Enthält Funktionen: {', '.join(funcs[:5])}")

    if purpose:
        desc.append(f"Vermutete Aufgabe: {', '.join(purpose)}")

    if not purpose:
        desc.append("Zweck unklar – benötigt weitere Analyse")

    return " | ".join(desc)

def run():

    print("\n[INVESTIGATE]\n")

    clusters = load(CLUSTERS)

    report = []

    for c in clusters:

        if c.get("size", 0) > 2:
            continue

        topic = c.get("topic")
        files = c.get("files", [])

        for f in files:

            content = read_file(f)
            if not content:
                continue

            funcs, classes = extract_structure(content)
            purpose = detect_purpose(content)

            desc = describe(f, funcs, classes, purpose)

            print("→", f)
            print(" ", desc)

            report.append({
                "file": f,
                "functions": funcs,
                "classes": classes,
                "purpose": purpose,
                "description": desc
            })

    with open(OUT, "w") as f:
        json.dump(report, f, indent=2)

    print("\n[INVESTIGATE] done:", len(report))

if __name__ == "__main__":
    run()
