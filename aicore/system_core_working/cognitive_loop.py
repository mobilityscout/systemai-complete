import json, os, time, subprocess

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode()
    except:
        return ""

def perception():
    return run("python3 /root/aicore/scanner.py")

def attention():
    return run("python3 /root/aicore/worker.py")

def thinking():
    return run("python3 /root/aicore/semantic_engine.py")

def memory():
    try:
        return json.load(open("/root/aicore/state.json"))
    except:
        return {}

def decision(state):

    total = state.get("stats", {}).get("total",0)
    high = state.get("stats", {}).get("high_value",0)

    if high < 50:
        return "focus_expand"

    if high > 50:
        return "refine"

    return "idle"

def act(action):

    if action == "focus_expand":
        return run("python3 /root/aicore/integration_engine.py")

    if action == "refine":
        return run("python3 /root/aicore/module_understanding.py")

    return "idle"

def loop():

    print("\n=== COGNITIVE LOOP ===")

    perception()
    attention()

    state = memory()

    print("STATE:", state.get("stats"))

    action = decision(state)

    print("DECISION:", action)

    result = act(action)

    print("ACTION RESULT:", result)

if __name__ == "__main__":
    while True:
        loop()
        time.sleep(15)
