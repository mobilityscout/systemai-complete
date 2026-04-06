import os

def execute(task):
    print("[WORKER] executing:", task)

    path = "/root/aicore/" + task["target"]
    os.makedirs(os.path.dirname(path), exist_ok=True)

    code = task.get("code")

    if not code:
        code = f"""def run():
    print("running {task['target']}")

if __name__ == "__main__":
    run()
"""

    with open(path, "w") as f:
        f.write(code)

    print("[WORKER] built:", path)
