import json

GOAL = "/root/aicore/goal.json"

def run():
    try:
        data = json.load(open(GOAL))
    except:
        data = {"goal": "idle"}

    print("[PRINCIPLE] current goal:", data.get("goal"))

def set_goal(text):
    json.dump({"goal": text}, open(GOAL, "w"), indent=2)
    print("[PRINCIPLE] new goal set:", text)

if __name__ == "__main__":
    while True:
        g = input("goal> ").strip()
        if not g:
            continue
        set_goal(g)
