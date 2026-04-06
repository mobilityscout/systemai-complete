import os, json

BASES = [
    "/root/system_modules",
    "/root/aicore",
    "/root/api"
]

OUTPUT = "/root/aicore/structure.json"

def summarize_file(path):
    try:
        with open(path, "r", errors="ignore") as f:
            content = f.read(300)
    except:
        return {"type":"unknown","summary":"unreadable"}

    if "def " in content or "function" in content:
        return {"type":"code","summary":"contains functions"}

    if "bash" in content or "#!/bin/bash" in content:
        return {"type":"script","summary":"shell script"}

    if "import" in content:
        return {"type":"module","summary":"imports detected"}

    return {"type":"unknown","summary":"no clear structure"}

def scan_dir(base):

    tree = {
        "path": base,
        "files": [],
        "children": []
    }

    try:
        items = os.listdir(base)
    except:
        return tree

    for item in items:

        path = os.path.join(base, item)

        if os.path.isfile(path):

            tree["files"].append({
                "name": item,
                "info": summarize_file(path)
            })

        elif os.path.isdir(path):

            tree["children"].append(scan_dir(path))

    return tree

def run():

    full = []

    for b in BASES:
        if os.path.exists(b):
            full.append(scan_dir(b))

    json.dump(full, open(OUTPUT,"w"))

    return {"built": len(full)}

if __name__ == "__main__":
    print(json.dumps(run()))
