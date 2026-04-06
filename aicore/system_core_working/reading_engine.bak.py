import os, json

def read_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(500)
    except:
        return ""

# 🧠 VERTIKAL
def vertical_analysis(path):
    content = read_file(path)

    summary = content[:120].replace("\n"," ")

    intent = "unknown"
    if "server" in content:
        intent = "server_logic"
    elif "fix" in content or "patch" in content:
        intent = "repair_logic"
    elif "api" in content:
        intent = "api_logic"

    return {
        "file": path,
        "summary": summary,
        "intent": intent
    }

# 🧠 HORIZONTAL
def horizontal_analysis(items):
    groups = {}

    for i in items:
        key = i["intent"]

        if key not in groups:
            groups[key] = []

        groups[key].append(i["file"])

    return groups

# 🔁 REKURSIV (einfacher Start)
def recursive_structure(groups):
    structured = {}

    for k,v in groups.items():
        structured[k] = {
            "count": len(v),
            "files": v[:10]
        }

    return structured

# 🧠 HAUPTENGINE
def run(base="/root"):
    results = []

    for root, dirs, files in os.walk(base):
        for f in files:
            path = os.path.join(root, f)
            results.append(vertical_analysis(path))

    horizontal = horizontal_analysis(results)
    structured = recursive_structure(horizontal)

    return {
        "structure": structured,
        "total_files": len(results)
    }

if __name__ == "__main__":
    print(json.dumps(run()))
