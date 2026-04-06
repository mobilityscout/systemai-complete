import json

GRAPH = "/root/aicore/graph.json"
INDEX = "/root/aicore/index.json"

def load():
    return json.load(open(GRAPH)), json.load(open(INDEX))

def find_module(name):

    g,i = load()

    return i["by_module"].get(name, [])

def find_logic():

    g,i = load()
    return i["by_type"]["logic"]

def find_structure():

    g,i = load()
    return i["by_type"]["structure"]

def run():

    g,i = load()

    return {
        "modules": list(i["by_module"].keys()),
        "logic_files": len(i["by_type"]["logic"]),
        "structure_files": len(i["by_type"]["structure"])
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
