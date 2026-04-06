import json, os

TODO = "/root/aicore/todo.json"
BASE = "/root/aicore/workspace"

def load():
    try: return json.load(open(TODO))
    except: return []

def save(d):
    json.dump(d, open(TODO,"w"), indent=2)

def run():
    tasks = load()

    if not tasks:
        print("[EXECUTOR] idle")
        return

    for t in tasks:
        name = t["target"].split("/")[-1].replace(".py","")
        path = BASE + "/" + t["target"].split("workspace/")[-1]

        os.makedirs(os.path.dirname(path), exist_ok=True)

        # DB
        if path.endswith(".db"):
            open(path,"w").close()

        # MODULE (🔥 FIXED IMPORT)
        elif "customer" in path or "billing" in path or "core" in path:
            open(path,"w").write(f"""
from .registry import register

def handler():
    return {{"module":"{name}","status":"ok"}}

register("/{name}", handler)
""")

        # IMPORT
        elif "import_" in path:
            open(path,"w").write("""
from .registry import register

def handler():
    return {"import":"ok"}

register("/import", handler)
""")

        # API
        elif "api.py" in path:
            open(path,"w").write("""
from .router import route
from .loader import load_all

load_all()

def handle(path):
    return route(path)
""")

        else:
            open(path,"w").write("# integrated")

        print("[EXECUTOR] integrated:", path)

    save([])
