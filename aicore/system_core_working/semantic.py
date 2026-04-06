import os, json

PATHS = [
    "/root/system_modules",
    "/root/system_auto",
    "/root/quarantine",
    "/root/generated"
]

def read_head(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(300)
    except:
        return ""

def classify(path):
    name = path.lower()
    content = read_head(path)

    if "chat" in name or "http.createServer" in content:
        return "chat_component"

    if "express" in content or "fastapi" in content or "api" in name:
        return "api_component"

    if "fix" in name or "patch" in name or "repair" in name:
        return "repair_script"

    if "log" in name:
        return "log"

    if path.endswith((".py",".js",".sh")):
        return "code"

    return "unknown"

def score(t):
    return {
        "chat_component": 1.0,
        "api_component": 0.9,
        "repair_script": 0.8,
        "code": 0.6,
        "unknown": 0.3,
        "log": 0.1
    }.get(t,0.2)

def belongs(t):
    return t in ["chat_component","api_component","repair_script","code"]

def scan():
    tree = {}

    for base in PATHS:
        if not os.path.exists(base):
            continue

        tree[base] = []

        for root, dirs, files in os.walk(base):
            for f in files:
                path = os.path.join(root, f)

                t = classify(path)

                tree[base].append({
                    "file": path,
                    "type": t,
                    "score": score(t),
                    "belongs_to_ai": belongs(t)
                })

    return tree

if __name__ == "__main__":
    print(json.dumps(scan()))
