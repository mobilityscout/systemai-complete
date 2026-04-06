import json

DB = "/root/aicore/knowledge.json"

def load():
    try:
        return json.load(open(DB))
    except:
        return {}

def save(data):
    json.dump(data, open(DB, "w"), indent=2)

def remember(goal, plan):
    data = load()
    data[goal] = plan
    save(data)
    print("[KNOWLEDGE] stored:", goal)

def recall(goal):
    data = load()
    return data.get(goal)
