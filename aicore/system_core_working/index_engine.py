import json

MEMORY = "/root/aicore/memory.json"
INDEX  = "/root/aicore/index.json"

def run():

    mem = json.load(open(MEMORY))

    index = {
        "by_module": {},
        "by_type": {
            "logic": [],
            "structure": []
        }
    }

    for f,info in mem["files"].items():

        m = info["module"]

        if m not in index["by_module"]:
            index["by_module"][m] = []

        index["by_module"][m].append(f)

        if info["data"]["functions"] > 0:
            index["by_type"]["logic"].append(f)

        if info["data"]["classes"] > 0:
            index["by_type"]["structure"].append(f)

    json.dump(index, open(INDEX,"w"))

    return {
        "modules": len(index["by_module"])
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
