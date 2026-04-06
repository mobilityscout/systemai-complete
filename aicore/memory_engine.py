import json
import time

MEMORY = "/root/aicore/memory.json"

def load():
    try:
        return json.load(open(MEMORY))
    except:
        return []

def save(data):
    json.dump(data, open(MEMORY, "w"), indent=2)

def log(event):
    data = load()

    data.append({
        "time": time.time(),
        "event": event
    })

    save(data)

def recent_failures(file, limit=10):
    data = load()[-limit:]

    fails = 0
    for e in data:
        ev = e.get("event", {})
        if ev.get("type") == "fix" and ev.get("file") == file:
            if ev.get("result") == "failed":
                fails += 1

    return fails
