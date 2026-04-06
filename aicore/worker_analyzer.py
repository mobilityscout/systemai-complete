import os

BASE = "/root/aicore"

def run(task):
    print("[ANALYZER] checking:", task)

    path = os.path.join(BASE, task.get("target"))

    if os.path.exists(path):
        print("[ANALYZER] OK:", path)
        return True

    print("[ANALYZER] FAIL:", path)
    return False
