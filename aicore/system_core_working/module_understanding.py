import os, json

BASE = "/root/aicore/system_core/modules"

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(800)
    except:
        return ""

def analyze_file(path):

    content = read_file(path)

    info = {
        "functions": 0,
        "classes": 0,
        "imports": 0
    }

    info["functions"] = content.count("def ")
    info["classes"] = content.count("class ")
    info["imports"] = content.count("import ")

    return info

def summarize_module(path):

    files = [f for f in os.listdir(path) if f.endswith(".py")]

    total_funcs = 0
    total_classes = 0
    total_imports = 0

    for f in files:
        data = analyze_file(os.path.join(path, f))

        total_funcs += data["functions"]
        total_classes += data["classes"]
        total_imports += data["imports"]

    # 🧠 SEMANTIK (grob, aber wichtig)
    purpose = "unknown"

    if total_funcs > 20:
        purpose = "logic heavy system"

    if total_classes > 5:
        purpose = "structured application"

    if total_imports > 10:
        purpose = "integrated system"

    # 📘 DIDAKTIK
    description = f"This module contains {len(files)} files, {total_funcs} functions and {total_classes} classes."

    completion = min(100, total_funcs + total_classes * 5)

    return {
        "module": path,
        "files": len(files),
        "functions": total_funcs,
        "classes": total_classes,
        "imports": total_imports,
        "purpose": purpose,
        "description": description,
        "completion": completion
    }

def run():

    results = []

    for m in os.listdir(BASE):

        path = os.path.join(BASE, m)

        if os.path.isdir(path):
            results.append(summarize_module(path))

    return results

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
