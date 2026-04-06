# === BOOTSTRAP FIRST ===
import os, sys

base = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(base)

for p in [base, parent]:
    if p not in sys.path:
        sys.path.insert(0, p)

print("[BOOTSTRAP] sys.path:", sys.path[:2])

# === IMPORTS ===
try:
    from state_core_engine import StateCore
except:
    from aicore.state_core_engine import StateCore

# === MINIMAL START ===
if __name__ == "__main__":
    print("[AI MANAGER] boot ok")

# === SELF BUILD PHASE ===
try:
    print("[AI MANAGER] starting analysis...")

    from organized.reading_engine import run as analyze

    data = analyze("/root/aicore")

    builder = None

    for deps in data.get("horizontal", {}).get("dependencies", {}).values():
        for f in deps:
            if "self_build.py" in f:
                builder = f
                break
        if builder:
            break

    if builder:
        print("[AI MANAGER] builder found:", builder)

        import importlib.util

        spec = importlib.util.spec_from_file_location("self_build", builder)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        print("[AI MANAGER] builder loaded")

    else:
        print("[AI MANAGER] builder not found")

except Exception as e:
    print("[AI MANAGER] self-build failed:", e)

# === END ===


# === ACTIVATE COGNITIVE LOOP ===
try:
    print("[AI MANAGER] activating cognition...")

    import importlib.util

    cog_path = "/root/aicore/system_core/cognitive_loop.py"

    spec = importlib.util.spec_from_file_location("cognitive_loop", cog_path)
    cog = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cog)

    if hasattr(cog, "loop"):
        print("[AI MANAGER] cognitive loop found → starting")
        cog.loop()
    else:
        print("[AI MANAGER] no loop() in cognitive module")

except Exception as e:
    print("[AI MANAGER] cognition failed:", e)

# === END ===


# === DYNAMIC MODULE RESOLVER ===
try:
    print("[AI MANAGER] resolving modules...")

    import os

    base = "/root/aicore"

    def find_file(name):
        for root, dirs, files in os.walk(base):
            if name in files:
                return os.path.join(root, name)
        return None

    required = ["scanner.py", "worker.py", "integration_engine.py"]

    resolved = {}

    for r in required:
        path = find_file(r)
        resolved[r] = path
        print(f"[RESOLVE] {r} -> {path}")

except Exception as e:
    print("[RESOLVE] failed:", e)

# === END ===


# === APPLY RESOLVED PATHS ===
try:
    print("[AI MANAGER] applying path corrections...")

    import subprocess

    mapping = {
        "scanner.py": "/root/aicore/system_core/scanner.py",
        "worker.py": "/root/aicore/system_core/worker.py",
        "integration_engine.py": "/root/aicore/system_core/integration_engine.py"
    }

    for name, path in mapping.items():
        if path:
            print(f"[PATCH] replacing {name} → {path}")

except Exception as e:
    print("[PATCH] failed:", e)

# === END ===


# === AUTO ORGANIZER ===
try:
    print("[AI MANAGER] organizing fragments...")

    import shutil, os

    base = "/root/aicore"
    target = {
        "core": base + "/system_core",
        "extensions": base + "/extensions",
        "apps": base + "/apps",
        "quarantine": base + "/quarantine",
        "unknown": base + "/unknown"
    }

    for t in target.values():
        os.makedirs(t, exist_ok=True)

    def classify(path):
        if "organized" in path:
            return None
        if "core" in path:
            return "core"
        if "api" in path or "app" in path:
            return "apps"
        if "test" in path or "backup" in path:
            return "quarantine"
        return "unknown"

    for root, dirs, files in os.walk(base):
        for f in files:
            if not f.endswith(".py"):
                continue

            full = os.path.join(root, f)

            if "organized" in full:
                continue

            category = classify(full)

            if category and category in target:
                dest = os.path.join(target[category], f)

                if not os.path.exists(dest):
                    try:
                        shutil.copy(full, dest)
                        print(f"[MOVE] {f} → {category}")
                    except:
                        pass

except Exception as e:
    print("[ORGANIZER] failed:", e)

# === END ===

