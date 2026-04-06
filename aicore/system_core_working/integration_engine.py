import json, os, shutil

STATE = "/root/aicore/state.json"
TODO = "/root/aicore/todo.json"
TARGET = "/root/aicore/system_core"

def load(path, default):
    try:
        return json.load(open(path))
    except:
        return default

def save(path, data):
    json.dump(data, open(path,"w"))

def classify(path):

    name = path.lower()

    # 🔥 SYSTEM CORE BEREICHE
    if any(x in path for x in [
        "/root/aicore",
        "/root/api",
        "/root/system_modules/core",
        "/root/system_modules/api"
    ]):
        return "core"

    # 🟡 PATCH / FIX
    if "fix" in name or "patch" in name:
        return "candidate"

    # ⚫ REST
    return "ignore"

def run():

    state = load(STATE, {})
    todo = load(TODO, [])

    integrated = []
    added = []

    for f,score in state.get("files", {}).items():

        if score < 0.5:
            continue

        if not os.path.exists(f):
            continue

        cls = classify(f)

        name = f.replace("/","_")
        dst = os.path.join(TARGET, name)

        if cls == "core":

            if not os.path.exists(dst):
                try:
                    shutil.copy(f, dst)
                    integrated.append(f)
                except:
                    pass

        elif cls == "candidate":

            entry = {
                "file": f,
                "score": score,
                "status": "pending"
            }

            if entry not in todo:
                todo.append(entry)
                added.append(f)

    save(TODO, todo)

    return {
        "integrated": len(integrated),
        "todo_added": len(added)
    }

if __name__ == "__main__":
    print(json.dumps(run()))
