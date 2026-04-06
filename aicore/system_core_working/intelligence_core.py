import os, json, re

BASE = "/root/aicore"
CTX_PATH = "/root/aicore/context_memory.json"
BRAIN_PATH = "/root/aicore/brain.json"

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(2000)
    except:
        return ""

def extract_structure(content):
    functions = re.findall(r'def (\w+)\(', content)
    classes = re.findall(r'class (\w+)', content)
    imports = re.findall(r'import (\w+)', content)
    return functions, classes, imports

def classify(functions, classes, imports):
    caps = []

    if functions:
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
    short = content[:120].replace("\n"," ")
    detail = content[:400].replace("\n"," ")
    return short, detail

def evaluate(caps, functions, classes):
    score = len(caps)*2 + len(functions) + len(classes)

    if not caps:
        maturity = "unknown"
    elif len(caps) == 1:
        maturity = "partial"
    else:
        maturity = "usable"

    return score, maturity

def run():
    print("[INTEL] loading context...")

    if not os.path.exists(CTX_PATH):
        print("[INTEL] no context")
        return

    with open(CTX_PATH, "r") as f:
        ctx = json.load(f)

    files = ctx.get("files", [])
    brain = {}

    print("[INTEL] analyzing:", len(files))

    for path in files:
        content = read_file(path)

        functions, classes, imports = extract_structure(content)
        caps = classify(functions, classes, imports)
        short, detail = summarize(content)
        score, maturity = evaluate(caps, functions, classes)

        brain[path] = {
            "short": short,
            "detail": detail,
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "capabilities": caps,
            "score": score,
            "maturity": maturity
        }

    with open(BRAIN_PATH, "w") as f:
        json.dump(brain, f, indent=2)

    print("[INTEL] brain built:", len(brain))

if __name__ == "__main__":
    run()
