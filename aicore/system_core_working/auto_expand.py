import json, os, shutil

STATE = "/root/aicore/state.json"
TARGET = "/root/aicore/expanded"

def run():
    try:
        s = json.load(open(STATE))
    except:
        return {"expanded":0}

    os.makedirs(TARGET, exist_ok=True)

    expanded = []

    for f,score in s["files"].items():

        if score > 0.4 and f.startswith("/root/aicore"):

            dst = TARGET + "/" + f.replace("/","_")

            try:
                shutil.copy(f,dst)
                expanded.append(f)
            except:
                pass

    return {
        "expanded": len(expanded)
    }

if __name__ == "__main__":
    print(json.dumps(run()))
