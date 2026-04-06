import json, os, shutil

STATE = "/root/aicore/state.json"
TARGET = "/root/aicore/imported"

def run():
    try:
        state = json.load(open(STATE))
    except:
        return {"imported": 0}

    os.makedirs(TARGET, exist_ok=True)

    imported = []
    skipped = []

    for f,score in state.get("files", {}).items():

        # 🔥 nur gute Dateien
        if score < 0.5:
            continue

        if not os.path.exists(f):
            continue

        name = f.replace("/","_")
        dst = os.path.join(TARGET, name)

        if os.path.exists(dst):
            skipped.append(f)
            continue

        try:
            shutil.copy(f, dst)
            imported.append(f)
        except:
            pass

    return {
        "imported": len(imported),
        "skipped": len(skipped)
    }

if __name__ == "__main__":
    print(json.dumps(run()))
