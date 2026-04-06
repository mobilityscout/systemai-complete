import threading, subprocess, time, json

def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True).decode()
    except:
        return ""

def get_attention():
    try:
        return json.loads(run("python3 /root/aicore/attention_controller.py"))
    except:
        return {}

def loop():

    while True:

        att = get_attention()

        print("\n🎯 ATTENTION:", att)

        if att.get("perception"):
            print("👁 perception")
            run("python3 /root/aicore/scanner.py")

        if att.get("attention"):
            print("🔍 attention")
            run("python3 /root/aicore/worker.py")

        if att.get("thinking"):
            print("🧠 thinking")
            run("python3 /root/aicore/semantic_engine.py")

        if att.get("integration"):
            print("⚙ integration")
            print(run("python3 /root/aicore/integration_engine.py"))

        time.sleep(5)

if __name__ == "__main__":
    loop()
