import os, json

PATHS = [
    "/root/quarantine",
    "/root/system_auto",
    "/root/generated"
]

def classify(path):
    name = path.lower()

    if "fix" in name or "patch" in name:
        return "maybe_useful"

    if name.endswith(".sh") or name.endswith(".py") or name.endswith(".js"):
        return "code"

    if "backup" in name or "snapshot" in name:
        return "backup"

    return "unknown"

def analyze():
    result = []

    for base in PATHS:
        if not os.path.exists(base):
            continue

        for root, dirs, files in os.walk(base):
            for f in files:
                path = os.path.join(root, f)

                result.append({
                    "file": path,
                    "type": classify(path)
                })

    return result

if __name__ == "__main__":
    print(json.dumps(analyze()))
