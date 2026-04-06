import memory_engine
import os

BASE = "/root/aicore/workspace"

def successful_upgrades(limit=20):
    data = memory_engine.load()[-limit:]

    files = []
    for e in data:
        ev = e.get("event", {})
        if ev.get("type") == "upgrade":
            files.append(ev.get("from"))

    return files

def extract_patterns(files):
    patterns = {
        "has_healthcheck": 0,
        "has_print": 0,
        "has_function": 0
    }

    for f in files:
        path = os.path.join(BASE, f)
        try:
            content = open(path).read()

            if "healthcheck" in content:
                patterns["has_healthcheck"] += 1
            if "print(" in content:
                patterns["has_print"] += 1
            if "def " in content:
                patterns["has_function"] += 1

        except:
            continue

    return patterns

def learn():
    files = successful_upgrades()

    if not files:
        return {}

    patterns = extract_patterns(files)

    print("[LEARN] patterns:", patterns)

    return patterns
