print('[LOG] start')
import subprocess, json

def health():
    try:
        out = subprocess.check_output("curl -s http://localhost/health", shell=True)
        return "ok"
    except:
        return "down"

def repair():
    subprocess.call("pkill -f server.js", shell=True)
    subprocess.Popen("node /root/api/server.js &", shell=True)

def run():
    state = health()

    if state == "down":
        repair()
        return {"status": "restarted"}

    return {"status": "ok"}

if __name__ == "__main__":
    print(json.dumps(run()))
