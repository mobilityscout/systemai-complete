import json

GOAL = "/root/aicore/goal.json"

def set_goal(g):
    json.dump({"goal": g}, open(GOAL, "w"))
    print("[INTERFACE] goal set:", g)

def show():
    try:
        print(json.load(open(GOAL)))
    except:
        print("no goal")

if __name__ == "__main__":
    while True:
        cmd = input(">> ")

        if cmd.startswith("goal "):
            set_goal(cmd.replace("goal ", ""))
        elif cmd == "show":
            show()
