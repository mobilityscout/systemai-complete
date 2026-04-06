import json

INDEX = "/root/aicore/index.json"
MEM   = "/root/aicore/memory.json"

def load():
    return json.load(open(INDEX)), json.load(open(MEM))

def answer(q):

    index, mem = load()
    q = q.lower()

    result = []

    # 🔍 einfache semantische Suche
    for f,info in mem["files"].items():

        if q in f.lower() or q in info["module"].lower():
            result.append({
                "file": f,
                "module": info["module"],
                "functions": info["data"]["functions"],
                "classes": info["data"]["classes"]
            })

    return result[:5]

def chat():

    while True:

        q = input("\n🧠 ASK: ")

        if q == "exit":
            break

        res = answer(q)

        print("\n💬 ANSWER:")

        for r in res:
            print(f"- {r['file']} ({r['module']})")

if __name__ == "__main__":
    chat()
