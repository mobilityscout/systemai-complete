import os, json

ROOT = "/root"

IGNORE = ["aicore","api","system_modules","quarantine","memory","generated","organized"]

def scan():
    files = []
    for f in os.listdir(ROOT):
        if f in IGNORE:
            continue

        path = os.path.join(ROOT, f)

        if os.path.isfile(path):
            files.append(f)

    return files

def classify(name):
    n = name.lower()

    if "fix" in n or "patch" in n:
        return "patch"

    if "api" in n:
        return "api"

    if name.endswith(".sh") or name.endswith(".py") or name.endswith(".js"):
        return "code"

    return "unknown"

def think():
    items = scan()

    stats = {
        "total": len(items),
        "patch": 0,
        "unknown": 0,
        "api": 0,
        "code": 0
    }

    for i in items:
        t = classify(i)
        stats[t] += 1

    return {
        "decision": "analyze_system",
        "summary": stats
    }

if __name__ == "__main__":
    print(json.dumps(think()))
