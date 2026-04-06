import os
import subprocess
import memory_engine

def syntax_ok(path):
    r = subprocess.run(["python3", "-m", "py_compile", path],
                       capture_output=True)
    return r.returncode == 0

def run(task):
    path = os.path.join("/root/aicore", task.get("target"))

    print("[FIXER] fixing:", path)

    if syntax_ok(path):
        memory_engine.log({
            "type": "fix",
            "file": path,
            "result": "no_issue"
        })
        return True

    # nicht reparierbar
    memory_engine.log({
        "type": "fix",
        "file": path,
        "result": "failed"
    })

    print("[FIXER] cannot repair → rebuild required")
    return False
