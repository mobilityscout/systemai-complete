import os, json

def read(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(500)
    except:
        return ""

def analyze(path):

    content = read(path)
    name = path.lower()

    result = {
        "file": path,
        "purpose": "unknown",
        "type": "unknown",
        "belongs_to_system": False,
        "usable": False,
        "risk": "low",
        "completion": 0
    }

    # 🔍 TYPE
    if ".py" in name or ".js" in name:
        result["type"] = "code"

    elif ".sh" in name:
        result["type"] = "script"

    # 🔍 PURPOSE
    if "server" in name:
        result["purpose"] = "backend service"

    elif "fix" in name or "patch" in name:
        result["purpose"] = "repair script"

    elif "ai" in name:
        result["purpose"] = "ai component"

    # 🔍 SYSTEM ZUGEHÖRIGKEIT
    if "aicore" in path or "api" in path:
        result["belongs_to_system"] = True

    # 🔍 USABLE
    if "def " in content or "function" in content:
        result["usable"] = True
        result["completion"] = 60

    # 🔍 RISK
    if "rm " in content or "sudo" in content:
        result["risk"] = "high"

    if result["usable"]:
        result["completion"] += 20

    return result

def run(base="/root"):

    findings = []

    for root, dirs, files in os.walk(base):
        for f in files:
            path = os.path.join(root, f)
            findings.append(analyze(path))

    return findings

if __name__ == "__main__":
    print(json.dumps(run()))
