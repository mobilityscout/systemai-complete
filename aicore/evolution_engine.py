import os
import shutil
import subprocess
import time
import memory_engine
import compare_engine
import learning_engine

BASE = "/root/aicore/workspace"

def last_upgrade_time():
    events = memory_engine.load()
    for e in reversed(events):
        ev = e.get("event", {})
        if ev.get("type") == "upgrade":
            return e.get("time", 0)
    return 0

def can_upgrade(cooldown=10):
    return time.time() - last_upgrade_time() > cooldown

def next_version(base_name):
    i = 2
    while True:
        name = f"{base_name}_v{i}.py"
        if not os.path.exists(os.path.join(BASE, name)):
            return name
        i += 1

def generate_candidate(base_file):
    base_name = os.path.splitext(base_file)[0]
    new_file = next_version(base_name)
    path = os.path.join(BASE, new_file)

    # 🧠 LEARNING
    patterns = learning_engine.learn()

    code = "# Learned Candidate\n\n"

    # adaptive generation
    if patterns.get("has_function", 0) > 0:
        code += "def run():\n    print('running learned version')\n\n"

    if patterns.get("has_healthcheck", 0) > 0:
        code += "def healthcheck():\n    return {'status':'ok','learned':True}\n\n"

    if patterns.get("has_print", 0) > 0:
        code += "def info():\n    print('info active')\n\n"

    code += "if __name__ == '__main__':\n    run()\n"

    with open(path, "w") as f:
        f.write(code)

    print("[EVOLVE] learned candidate:", new_file)
    return new_file

def promote(base_file, candidate):
    shutil.copy(
        os.path.join(BASE, candidate),
        os.path.join(BASE, base_file)
    )

    print("[EVOLVE] promoted:", candidate, "→", base_file)

    memory_engine.log({
        "type": "upgrade",
        "from": candidate,
        "to": base_file
    })

def evolve(base_file="module.py"):
    if not can_upgrade():
        print("[EVOLVE] cooldown active → skip")
        return

    print("[EVOLVE] upgrading:", base_file)

    candidate = generate_candidate(base_file)

    if not compare_engine.compare(base_file, candidate):
        print("[EVOLVE] candidate worse → discard")
        return

    promote(base_file, candidate)
