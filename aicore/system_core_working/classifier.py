print('[LOG] start')
import os, shutil

ROOT = "/root"
TARGET = "/root/system_auto"

os.makedirs(TARGET, exist_ok=True)

def classify(name):
    n = name.lower()

    if "fix" in n or "patch" in n:
        return "patch"

    if "api" in n:
        return "api"

    if name.endswith(".sh") or name.endswith(".py") or name.endswith(".js"):
        return "code"

    return "unknown"

def run():
    moved = []

    for f in os.listdir(ROOT):
        if f in ["aicore","api","system_modules","quarantine","memory","system_auto"]:
            continue

        src = os.path.join(ROOT, f)

        if not os.path.isfile(src):
            continue

        t = classify(f)

        dest_dir = os.path.join(TARGET, t)
        os.makedirs(dest_dir, exist_ok=True)

        dst = os.path.join(dest_dir, f)

        shutil.move(src, dst)
        moved.append((f, t))

    return moved

if __name__ == "__main__":
    result = run()
    print(result)
