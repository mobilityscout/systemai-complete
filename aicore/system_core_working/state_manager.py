import json

STATE = "/root/aicore/state.json"

def load():
    try:
        with open(STATE, "r") as f:
            return json.load(f)
    except:
        return {
            "files": {},
            "stats": {
                "total": 0,
                "high_value": 0
            }
        }

def save(state):
    with open(STATE, "w") as f:
        json.dump(state, f)

def update(file, score):
    state = load()

    state["files"][file] = score

    state["stats"]["total"] = len(state["files"])
    state["stats"]["high_value"] = len(
        [v for v in state["files"].values() if v > 0.4]
    )

    save(state)
