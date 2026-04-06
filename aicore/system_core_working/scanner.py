print('[LOG] start')
import os, json

CONFIG = json.load(open("/root/aicore/config.json"))
BASE = CONFIG["base_path"]
MAX = CONFIG["max_files_per_scan"]

QUEUE = "/root/aicore/queue.json"

def load():
    try:
        return json.load(open(QUEUE))
    except:
        return []

def save(q):
    json.dump(q, open(QUEUE,"w"))

def run():
    q = load()
    count = 0

    for root, dirs, files in os.walk(BASE):
        for f in files:

            if count >= MAX:
                save(q)
                return

            path = os.path.join(root, f)

            if path not in q:
                q.append(path)
                count += 1

    save(q)

if __name__ == "__main__":
    run()
