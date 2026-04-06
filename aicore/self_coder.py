import os
import memory_engine

BASE = "/root/aicore/workspace"

def already_evolved():
    events = memory_engine.load()

    for e in reversed(events):
        ev = e.get("event", {})
        if ev.get("type") == "evolve":
            return True
    return False

def evolve():
    if already_evolved():
        print("[EVOLVE] already done → skip")
        return

    print("[EVOLVE] generating improved module")

    path = os.path.join(BASE, "module_improved.py")

    code = '''# Improved Module (AI Generated)

def run():
    print("improved execution")

def healthcheck():
    return {"status": "ok", "version": 2}

def new_feature():
    return "adaptive behavior active"

if __name__ == "__main__":
    run()
'''

    with open(path, "w") as f:
        f.write(code)

    memory_engine.log({
        "type": "evolve",
        "file": path,
        "result": "created"
    })

    print("[EVOLVE] created:", path)
