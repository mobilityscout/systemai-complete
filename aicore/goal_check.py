import os

BASE = "/root/aicore/workspace"

def goal_done(goal):
    if "api" in goal:
        required = ["api.py", "router.py", "handler.py"]
        return all(os.path.exists(os.path.join(BASE, f)) for f in required)

    if "system" in goal:
        required = ["module_a.py", "module_b.py"]
        return all(os.path.exists(os.path.join(BASE, f)) for f in required)

    return os.path.exists(os.path.join(BASE, "module.py"))
