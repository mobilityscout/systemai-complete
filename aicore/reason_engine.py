import os

BASE = "/root/aicore/workspace"

def analyze(file):
    path = os.path.join(BASE, file)

    try:
        content = open(path).read()
    except:
        return {}

    return {
        "functions": content.count("def "),
        "has_class": "class " in content,
        "has_healthcheck": "healthcheck" in content,
        "has_return": "return" in content,
        "lines": len(content.splitlines())
    }

def explain(base_file, candidate_file):
    b = analyze(base_file)
    c = analyze(candidate_file)

    reasons = []

    if c.get("functions", 0) > b.get("functions", 0):
        reasons.append("more functions")

    if c.get("lines", 0) > b.get("lines", 0):
        reasons.append("more code depth")

    if c.get("has_class") and not b.get("has_class"):
        reasons.append("uses class structure")

    if c.get("has_return") and not b.get("has_return"):
        reasons.append("better return logic")

    if c.get("has_healthcheck") and not b.get("has_healthcheck"):
        reasons.append("adds healthcheck")

    return reasons
