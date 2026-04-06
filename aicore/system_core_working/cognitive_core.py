import json, subprocess, time

STATE_FILE = "/root/aicore/cognitive_state.json"

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode()
    except:
        return ""

def load():
    try:
        return json.load(open(STATE_FILE))
    except:
        return {
            "perception": {},
            "attention": {},
            "memory": {},
            "thinking": {},
            "decision": {}
        }

def save(state):
    json.dump(state, open(STATE_FILE,"w"))

# 👁 PERCEPTION
def perception(state):
    run("python3 /root/aicore/scanner.py")
    state["perception"]["status"] = "updated"
    return state

# 🔍 ATTENTION
def attention(state):
    run("python3 /root/aicore/worker.py")

    try:
        mem = json.load(open("/root/aicore/state.json"))
        state["memory"] = mem["stats"]
    except:
        pass

    return state

# 🧠 THINKING
def thinking(state):
    if state["memory"].get("high_value",0) > 20:
        state["thinking"]["mode"] = "active"
    else:
        state["thinking"]["mode"] = "collecting"

    return state

# 🎯 DECISION
def decision(state):

    high = state["memory"].get("high_value",0)

    if high < 50:
        state["decision"]["action"] = "expand"
    else:
        state["decision"]["action"] = "refine"

    return state

# ⚙ ACTION
def act(state):

    action = state["decision"].get("action")

    if action == "expand":
        run("python3 /root/aicore/integration_engine.py")

    if action == "refine":
        run("python3 /root/aicore/module_understanding.py")

    return state

def loop():

    state = load()

    state = perception(state)
    state = attention(state)
    state = thinking(state)
    state = decision(state)
    state = act(state)

    save(state)

    print("\n🧠 COGNITIVE STATE")
    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    while True:
        loop()
        time.sleep(5)
