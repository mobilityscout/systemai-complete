import json, os, time

BRAIN = "/root/aicore/brain.json"

def load_brain():
    if not os.path.exists(BRAIN):
        return {}
    with open(BRAIN, "r") as f:
        return json.load(f)

def find_targets(brain):
    targets = []

    for path, data in brain.items():

        # neugier = unklare + mittlere module
        if data.get("decision") in ["review", "usable"]:
            targets.append((path, data.get("priority", 0)))

    # höchste priorität zuerst
    targets = sorted(targets, key=lambda x: x[1], reverse=True)

    return [t[0] for t in targets[:10]]

def inspect(path):
    try:
        with open(path, "r", errors="ignore") as f:
            content = f.read()

        lines = len(content.splitlines())

        return {
            "lines": lines,
            "has_classes": "class " in content,
            "has_functions": "def " in content
        }

    except:
        return {}

def run():

    print("[CURIOSITY] scanning...")

    brain = load_brain()

    if not brain:
        print("[CURIOSITY] no brain")
        return

    targets = find_targets(brain)

    print("[CURIOSITY] targets:", len(targets))

    for t in targets:
        info = inspect(t)

        print(" ->", t)
        print("    lines:", info.get("lines"))
        print("    class:", info.get("has_classes"))
        print("    func :", info.get("has_functions"))

    print("[CURIOSITY] done")

if __name__ == "__main__":
    run()
