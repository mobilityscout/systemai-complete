import os, json, subprocess

def check():
    issues = []

    if not os.path.exists("/root/api/server.js"):
        issues.append("missing_api")

    if not os.path.exists("/root/aicore/brain_entry.py"):
        issues.append("missing_brain")

    return issues

def fix(issue):
    if issue == "missing_api":
        return "echo 'API missing - manual restore needed'"

    if issue == "missing_brain":
        return "echo 'Brain missing - critical'"

    return None

def run():
    issues = check()
    actions = []

    for i in issues:
        cmd = fix(i)
        if cmd:
            subprocess.call(cmd, shell=True)
            actions.append(i)

    return {
        "issues": issues,
        "fixed": actions
    }

if __name__ == "__main__":
    print(json.dumps(run()))
