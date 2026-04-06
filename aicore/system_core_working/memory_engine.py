import os, json

MEMORY = "/root/aicore/memory.json"

def load():
    try:
        return json.load(open(MEMORY))
    except:
        return {
            "files": {},
            "modules": {},
            "relations": {}
        }

def save(mem):
    json.dump(mem, open(MEMORY,"w"))

def summarize(path):

    try:
        content = open(path, "r", errors="ignore").read(500)
    except:
        return None

    return {
        "functions": content.count("def "),
        "classes": content.count("class "),
        "imports": content.count("import "),
        "summary": content[:120]
    }

def detect_module(path):

    parts = path.split("/")

    if "aicore_backup" in parts:
        return "aicore_backup"

    if "api" in parts:
        return "api"

    return "unknown"

def run(base="/root/aicore/system_core/modules"):

    mem = load()

    for root, dirs, files in os.walk(base):

        for f in files:

            if not f.endswith(".py"):
                continue

            path = os.path.join(root, f)

            if path in mem["files"]:
                continue  # 🔥 NICHT neu lesen!

            data = summarize(path)

            if not data:
                continue

            module = detect_module(path)

            mem["files"][path] = {
                "module": module,
                "data": data
            }

            if module not in mem["modules"]:
                mem["modules"][module] = []

            mem["modules"][module].append(path)

    save(mem)

    return {
        "files": len(mem["files"]),
        "modules": len(mem["modules"])
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
