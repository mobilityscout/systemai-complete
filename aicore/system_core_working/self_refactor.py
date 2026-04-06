import os, json, shutil

REPORT = "/root/aicore/investigate_report.json"
QUEUE = "/root/aicore/action_queue.json"

def load():
    if not os.path.exists(REPORT):
        return []
    with open(REPORT, "r") as f:
        return json.load(f)

def propose_fix(item):

    fixes = []

    funcs = item.get("functions", [])
    path = item.get("file")

    # Beispiel: fehlendes logging
    if "run" in funcs:
        fixes.append({
            "type": "add_logging",
            "file": path
        })

    # Beispiel: fehlendes error handling
    if "fix" in funcs or "execute" in funcs:
        fixes.append({
            "type": "add_try_wrapper",
            "file": path
        })

    return fixes

def save_actions(actions):
    with open(QUEUE, "w") as f:
        json.dump(actions, f, indent=2)

def run():

    print("[REFACTOR] analyzing...")

    data = load()
    actions = []

    for item in data:
        fixes = propose_fix(item)
        actions.extend(fixes)

    if not actions:
        print("[REFACTOR] no improvements found")
        return

    print("[REFACTOR] proposals:", len(actions))

    for a in actions[:10]:
        print(" -", a)

    save_actions(actions)

if __name__ == "__main__":
    run()
