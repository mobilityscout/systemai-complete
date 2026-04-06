import json, os, shutil

ACTIONS = "/root/aicore/action_queue.json"
LOG = "/root/aicore/action_log.json"

def load():
    if not os.path.exists(ACTIONS):
        return []
    with open(ACTIONS, "r") as f:
        return json.load(f)

def save_log(entry):
    data = []
    if os.path.exists(LOG):
        with open(LOG, "r") as f:
            data = json.load(f)

    data.append(entry)

    with open(LOG, "w") as f:
        json.dump(data, f, indent=2)

def execute(action):

    typ = action.get("type")
    path = action.get("file")

    print("[ACTION]", typ, path)

    try:

        if typ == "archive":
            dst = "/root/aicore/trash_quarantine/" + os.path.basename(path)
            shutil.move(path, dst)

        elif typ == "create_backup":
            dst = path + ".bak"
            shutil.copy(path, dst)

        elif typ == "noop":
            pass

        result = "success"

    except Exception as e:
        result = str(e)

    save_log({
        "action": typ,
        "file": path,
        "result": result
    })

def run():

    print("[ACTION ENGINE] running...")

    actions = load()

    if not actions:
        print("[ACTION ENGINE] no actions")
        return

    for a in actions:
        execute(a)

    print("[ACTION ENGINE] done")

if __name__ == "__main__":
    run()
