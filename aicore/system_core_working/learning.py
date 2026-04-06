import json, os

MEM_FILE = "/root/memory/memory.json"

def load():
    try:
        with open(MEM_FILE,"r") as f:
            return json.load(f)
    except:
        return {"actions":{}, "learning":{}, "history":[]}

def save(m):
    os.makedirs("/root/memory", exist_ok=True)
    with open(MEM_FILE,"w") as f:
        json.dump(m,f,indent=2)

def evaluate(current):
    mem = load()

    history = mem.get("history", [])
    history.append(current["unknown"])

    # nur letzte 3 Werte betrachten
    history = history[-3:]
    mem["history"] = history

    learning = mem.get("learning", {})

    if len(history) >= 2:
        # Trend statt Einzelwert
        if history[-1] > history[0]:
            learning["cleanup_effective"] = False
        elif history[-1] < history[0]:
            learning["cleanup_effective"] = True
        else:
            # stabil → nicht ändern
            learning["cleanup_effective"] = learning.get("cleanup_effective", False)

    mem["learning"] = learning
    save(mem)

    return learning

if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())
    result = evaluate(data["summary"])
    print(json.dumps(result))
