import os, json, re

BASE = "/root/aicore"

CTX_PATH = BASE + "/context_memory.json"
MEM_PATH = BASE + "/memory.json"
BRAIN_PATH = BASE + "/brain.json"

# ----------------------------
# PHASE 1 — CONTEXT (STRUCTURE)
# ----------------------------
def build_context():
    files = []
    tree = {}

    for root, dirs, fs in os.walk(BASE):
        rel = root.replace(BASE, "") or "/"
        tree.setdefault(rel, [])

        for f in fs:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                files.append(path)
                tree[rel].append(f)

    ctx = {
        "total_files": len(files),
        "files": files,
        "structure": tree
    }

    with open(CTX_PATH, "w") as f:
        json.dump(ctx, f, indent=2)

    return ctx

# ----------------------------
# PHASE 2 — UNDERSTAND (READ)
# ----------------------------
def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(2000)
    except:
        return ""

def extract(content):
    funcs = re.findall(r'def (\w+)\(', content)
    classes = re.findall(r'class (\w+)', content)
    imports = re.findall(r'import (\w+)', content)
    return funcs, classes, imports

def classify(funcs, classes, imports):
    caps = []

    if funcs:
        caps.append("logic")
    if classes:
        caps.append("structure")
    if any("flask" in i or "app" in i for i in imports):
        caps.append("system")
    if any("memory" in i for i in imports):
        caps.append("memory")
    if any("semantic" in i or "analy" in i for i in imports):
        caps.append("analysis")

    return list(set(caps))

def summarize(content):
    return (
        content[:120].replace("\n"," "),
        content[:400].replace("\n"," ")
    )

# ----------------------------
# PHASE 3 — EVALUATE
# ----------------------------
def evaluate(caps, funcs, classes):
    score = len(caps)*2 + len(funcs) + len(classes)

    if not caps:
        maturity = "unknown"
    elif len(caps) == 1:
        maturity = "partial"
    else:
        maturity = "usable"

    return score, maturity

# ----------------------------
# RUN INTELLIGENCE
# ----------------------------
def run():

    print("[INTEL] phase 1 — context")
    ctx = build_context()

    files = ctx["files"]

    print("[INTEL] phase 2 — reading:", len(files))

    brain = {}

    for path in files:
        content = read_file(path)

        funcs, classes, imports = extract(content)
        caps = classify(funcs, classes, imports)
        short, detail = summarize(content)
        score, maturity = evaluate(caps, funcs, classes)

        brain[path] = {
            "short": short,
            "detail": detail,
            "functions": funcs,
            "classes": classes,
            "imports": imports,
            "capabilities": caps,
            "score": score,
            "maturity": maturity
        }

    print("[INTEL] phase 3 — saving")

    with open(BRAIN_PATH, "w") as f:
        json.dump(brain, f, indent=2)

    mem = {
        "total_files": ctx["total_files"],
        "domains": list(ctx["structure"].keys()),
        "brain_entries": len(brain)
    }

    with open(MEM_PATH, "w") as f:
        json.dump(mem, f, indent=2)

    print("[INTEL] done:", len(brain), "entries")

if __name__ == "__main__":
    run()
