import json
import threading
import worker_pool

TODO = "/root/aicore/todo.json"

def load():
    try:
        return json.load(open(TODO))
    except:
        return []

def save(data):
    json.dump(data, open(TODO, "w"), indent=2)

def run():
    tasks = load()

    if not tasks:
        print("[EXECUTOR] idle")
        return

    print("[EXECUTOR] running batch:", len(tasks))

    threads = []

    for task in tasks:
        t = threading.Thread(target=worker_pool.execute, args=(task,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    save([])
