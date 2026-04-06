import json, os

REPORT = "/root/aicore/principle_report.json"

def load():
    if not os.path.exists(REPORT):
        return {}
    with open(REPORT, "r") as f:
        return json.load(f)

def summarize(report):

    print("\n=== PRINCIPLE VIEW ===\n")

    print("Duplicates:", len(report.get("duplicates", [])))
    print("Garbage candidates:", len(report.get("garbage_candidates", [])))

    print("\nTop Garbage (preview):")
    for g in report.get("garbage_candidates", [])[:10]:
        print(" -", g)

    print("\nStructure Proposal:")
    for k, v in report.get("proposed_structure", {}).items():
        print(" ", k, ":", len(v))

def propose_actions(report):

    actions = []

    for f in report.get("duplicates", [])[:20]:
        actions.append({
            "file": f,
            "action": "review_duplicate"
        })

    for f in report.get("garbage_candidates", [])[:20]:
        actions.append({
            "file": f,
            "action": "review_delete"
        })

    return actions

def run():

    report = load()

    if not report:
        print("[PRINCIPLE] no report")
        return

    summarize(report)

    actions = propose_actions(report)

    print("\n=== SUGGESTED ACTIONS ===\n")

    for a in actions:
        print(a["action"], "→", a["file"])

if __name__ == "__main__":
    run()
