import json
import os

def load_brain():
    try:
        with open("/tmp/brain.json","r") as f:
            return json.load(f)
    except:
        return {}

def detect_issues(data):
    issues = []

    summary = data.get("summary", {})

    if summary.get("patch",0) > 20:
        issues.append("too_many_patches")

    if summary.get("unknown",0) > 10:
        issues.append("too_many_unknowns")

    return issues

def propose_actions(issues):
    actions = []

    if "too_many_patches" in issues:
        actions.append("consolidate_core")

    if "too_many_unknowns" in issues:
        actions.append("run_cleanup")

    return actions

def run():
    data = load_brain()

    issues = detect_issues(data)
    actions = propose_actions(issues)

    return {
        "issues": issues,
        "actions": actions
    }

if __name__ == "__main__":
    print(json.dumps(run()))
