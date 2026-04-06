print('[LOG] start')
import os, json

SEARCH_PATHS = [
    "/root",
    "/root/system_auto",
    "/root/generated",
    "/root/system_modules"
]

def find_files():
    found = []

    for base in SEARCH_PATHS:
        if not os.path.exists(base):
            continue

        for root, dirs, files in os.walk(base):
            for f in files:
                path = os.path.join(root, f)
                found.append(path)

    return found

def classify(path):
    name = path.lower()

    if "chat" in name:
        return "chat"

    if "api" in name:
        return "api"

    if name.endswith(".js") or name.endswith(".py"):
        return "code"

    return "other"

def run():
    files = find_files()

    result = {
        "total_files": len(files),
        "chat_modules": [],
        "api_modules": [],
        "code_files": []
    }

    for f in files:
        t = classify(f)

        if t == "chat":
            result["chat_modules"].append(f)

        elif t == "api":
            result["api_modules"].append(f)

        elif t == "code":
            result["code_files"].append(f)

    return result

if __name__ == "__main__":
    print(json.dumps(run()))
