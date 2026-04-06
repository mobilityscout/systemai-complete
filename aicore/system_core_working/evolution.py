import json, subprocess

def load_principle():
    with open("/root/aicore/principle.json") as f:
        return json.load(f)

def get_state():
    semantic = json.loads(
        subprocess.check_output("python3 /root/aicore/semantic.py", shell=True)
    )

    state = {
        "chat": 0,
        "api": 0,
        "repair": 0,
        "code": 0
    }

    for base in semantic:
        for f in semantic[base]:
            t = f.get("type")

            if t == "chat_component":
                state["chat"] += 1

            elif t == "api_component":
                state["api"] += 1

            elif t == "repair_script":
                state["repair"] += 1

            elif t == "code":
                state["code"] += 1

    return state

def evaluate(state):
    suggestions = []

    if state["chat"] == 0:
        suggestions.append("build_chat")

    if state["api"] < 2:
        suggestions.append("expand_api")

    if state["repair"] < 3:
        suggestions.append("improve_self_healing")

    if state["code"] < 5:
        suggestions.append("increase_modules")

    return suggestions

def run():
    state = get_state()
    suggestions = evaluate(state)

    return {
        "state": state,
        "suggestions": suggestions
    }

if __name__ == "__main__":
    print(json.dumps(run()))
