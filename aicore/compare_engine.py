import os
import subprocess
import reason_engine

BASE = "/root/aicore/workspace"

def run_file(path):
    try:
        r = subprocess.run(
            ["python3", path],
            capture_output=True,
            text=True,
            timeout=2
        )
        return r.stdout.strip(), r.returncode
    except:
        return "", 1

def score(file):
    path = os.path.join(BASE, file)

    try:
        content = open(path).read()
    except:
        return 0

    score = 0

    # Syntax
    r = subprocess.run(
        ["python3", "-m", "py_compile", path],
        capture_output=True
    )
    if r.returncode != 0:
        return 0

    score += 3

    # Execution
    out, code = run_file(path)
    if code == 0:
        score += 2

    # Output richness
    score += min(len(out) // 10, 3)

    # Structure
    score += content.count("def ")

    if "healthcheck" in content:
        score += 2

    if "return" in content:
        score += 1

    if "class " in content:
        score += 2

    return score

def compare(base_file, candidate_file):
    base_score = score(base_file)
    cand_score = score(candidate_file)

    print(f"[COMPARE] {base_file}: {base_score}")
    print(f"[COMPARE] {candidate_file}: {cand_score}")

    # 🧠 REASONING
    reasons = reason_engine.explain(base_file, candidate_file)

    if reasons:
        print("[REASON] candidate better because:", reasons)

    return cand_score > base_score
