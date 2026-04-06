import os, json

def read(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read()
    except:
        return ""

def analyze(path):
    content = read(path)

    lines = content.split("\n")

    functions = 0
    imports = 0
    commands = 0
    comments = 0

    for l in lines[:200]:

        l = l.strip()

        if l.startswith("def ") or l.startswith("function"):
            functions += 1

        if "import " in l or "require(" in l:
            imports += 1

        if "exec" in l or "run" in l or "bash" in l:
            commands += 1

        if l.startswith("#") or l.startswith("//"):
            comments += 1

    size = len(lines)

    # 🧠 ROLLEN ERKENNEN
    role = "unknown"

    if functions > 3:
        role = "logic"

    if commands > 2:
        role = "executor"

    if imports > 3:
        role = "module"

    if size < 10:
        role = "fragment"

    # 📊 MATURITY
    maturity = min(1.0, (functions + imports + commands) / 10)

    return {
        "file": path,
        "role": role,
        "functions": functions,
        "imports": imports,
        "commands": commands,
        "maturity": round(maturity,2)
    }

def scan(base="/root"):
    results = []

    for root, dirs, files in os.walk(base):
        for f in files:
            path = os.path.join(root, f)
            results.append(analyze(path))

    return results

if __name__ == "__main__":
    print(json.dumps(scan()))
