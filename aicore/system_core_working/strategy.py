import json

def decide(learning, summary):
    actions = []

    if learning.get("cleanup_effective") == False:
        if summary.get("unknown",0) > 10:
            actions.append("classify_unknowns")
            actions.append("organize_structure")

    return actions

if __name__ == "__main__":
    import sys
    data = json.loads(sys.stdin.read())

    learning = data.get("learning",{})
    summary = data.get("summary",{})

    print(json.dumps({
        "actions": decide(learning, summary)
    }))
