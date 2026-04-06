import os
import memory_engine

BASE = "/root/aicore"

def gen_code(task):
    name = os.path.splitext(os.path.basename(task.get("target")))[0]
    return f'''# Auto-generated module: {name}

def run():
    print("running {name}")

def healthcheck():
    return "ok"

if __name__ == "__main__":
    run()
'''

def run(task):
    path = os.path.join(BASE, task.get("target"))

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:
        f.write(gen_code(task))

    print("[BUILDER] created:", path)

    memory_engine.log({
        "type": "build",
        "file": path,
        "result": "success"
    })
