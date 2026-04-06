print('[LOG] start')
import json
from state_manager import update

QUEUE = "/root/aicore/queue.json"

MAX_BATCH = 10

def load():
    try:
        return json.load(open(QUEUE))
    except:
        return []

def save(q):
    json.dump(q, open(QUEUE,"w"))

def read(path):
    try:
        with open(path,"r",errors="ignore") as f:
            return f.read(200)
    except:
        return ""

def analyze(path):
    c = read(path)

    score = 0
    if "def " in c: score += 0.3
    if "import" in c: score += 0.3
    if "bash" in c: score += 0.2

    return round(score,2)

def run():
    q = load()

    if not q:
        return

    batch = q[:MAX_BATCH]
    q = q[MAX_BATCH:]

    for f in batch:
        score = analyze(f)
        update(f, score)

    save(q)

if __name__ == "__main__":
    run()
