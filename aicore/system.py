import time, brain, executor, threading

CURRENT_GOAL = {"goal":"maintain"}

def loop():
    print("[SYSTEM ACTIVE]")

    while True:
        print("\n--- LOOP ---")

        goal = CURRENT_GOAL["goal"]

        if goal != "maintain":
            brain.run(goal)
        else:
            print("[SYSTEM] idle")

        executor.run()

        time.sleep(2)

def chat():
    while True:
        cmd = input(">> ")

        if cmd:
            CURRENT_GOAL["goal"] = cmd
            print("[CHAT] goal:", cmd)

t1 = threading.Thread(target=loop)
t2 = threading.Thread(target=chat)

t1.start()
t2.start()
