import json, os

BASE = "/root/aicore/workspace"
TODO = "/root/aicore/todo.json"
MEMORY = "/root/aicore/memory.json"

def load(p, d):
    try: return json.load(open(p))
    except: return d

def save(p, d):
    json.dump(d, open(p,"w"), indent=2)

# 🧠 DOMAIN INTERPRETATION
def interpret(goal):
    g = goal.lower()

    domains = []

    if "customer" in g: domains.append("customer")
    if "billing" in g or "invoice" in g: domains.append("billing")
    if "product" in g: domains.append("product")
    if "import" in g: domains.append("import")

    if not domains:
        domains = ["core"]

    return domains

# 🧠 THINKING
def think(goal, domains):
    print("\n[THINKING]")

    print("- benötigt verteilte DB-Struktur")
    print("- benötigt Schema pro Domain")
    print("- benötigt Import-Logik")
    print("- benötigt API + Routing")
    print("- Domains:", domains)

# 🧠 PLAN GENERATOR
def plan(domains):
    tasks = []

    for d in domains:
        tasks.append({"type":"build","target":f"workspace/{d}.db"})
        tasks.append({"type":"build","target":f"workspace/{d}_schema.sql"})
        tasks.append({"type":"build","target":f"workspace/import_{d}.py"})

    # shared layer
    tasks.append({"type":"build","target":"workspace/registry.py"})
    tasks.append({"type":"build","target":"workspace/router.py"})
    tasks.append({"type":"build","target":"workspace/api.py"})

    return tasks

def run(goal):
    print("[BRAIN] goal:", goal)

    tasks = load(TODO, [])
    if tasks:
        print("[BRAIN] executing existing tasks")
        return

    domains = interpret(goal)
    think(goal, domains)

    tasks = plan(domains)

    print("\n[PLAN]")
    for t in tasks:
        print("-", t["target"])

    save(TODO, tasks)

    mem = load(MEMORY, [])
    mem.append({"goal":goal, "domains":domains})
    save(MEMORY, mem)
