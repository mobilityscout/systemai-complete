import os, json

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(2000)
    except:
        return ""

# 🧠 VERTIKAL (ECHT)
def vertical_analysis(path):
    content = read_file(path)

    functions = []
    classes = []
    imports = []

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("def "):
            functions.append(line.split("(")[0].replace("def ",""))

        elif line.startswith("class "):
            classes.append(line.split(":")[0].replace("class ",""))

        elif line.startswith("import ") or line.startswith("from "):
            imports.append(line)

    return {
        "file": path,
        "functions": functions,
        "classes": classes,
        "imports": imports
    }

# 🧠 HORIZONTAL (ECHT)
def horizontal_analysis(items):
    deps = {}
    func_map = {}

    for i in items:
        for imp in i.get("imports", []):
            deps.setdefault(imp, []).append(i["file"])

        for fn in i.get("functions", []):
            func_map.setdefault(fn, []).append(i["file"])

    return {
        "dependencies": deps,
        "function_overlap": func_map
    }

def recursive_structure(groups):
    return groups

# 🧠 HAUPTENGINE
def run(base="/root/aicore"):
    results = []

    for root, dirs, files in os.walk(base):
        for f in files:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                results.append(vertical_analysis(path))

    horizontal = horizontal_analysis(results)

    return {
        "horizontal": horizontal,
        "total_files": len(results)
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
