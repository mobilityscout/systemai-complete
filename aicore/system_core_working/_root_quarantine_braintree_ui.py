from flask import Flask
import os

app = Flask(__name__)

BASE = os.path.expanduser("~/braintree")

def read_file(path):
    if not os.path.exists(path):
        return "EMPTY"
    return open(path).read()

@app.route("/")
def index():
    lock = os.path.exists(BASE + "/LOCK")

    report = read_file(BASE + "/lab/runs/run-latest/report.log")
    analysis = read_file(BASE + "/lab/analysis.log")

    return f"""
    <h1>Braintree Control UI</h1>

    <h2>System Status</h2>
    <pre>{'LOCKED' if lock else 'UNLOCKED'}</pre>

    <h2>Reading Protocol</h2>
    <pre>
STEP 1: Vertical
STEP 2: Horizontal
    </pre>

    <h2>Braintree Log</h2>
    <pre>{report}</pre>

    <h2>Labor Analysis</h2>
    <pre>{analysis}</pre>

    <h2>IAM Required</h2>
    <form action="/unlock" method="post">
        <button>CONFIRM REPAIR</button>
    </form>
    """

@app.route("/unlock", methods=["POST"])
def unlock():
    os.system("~/braintree/unlock.sh")
    return "<h2>UNLOCKED</h2><a href='/'>Back</a>"

app.run(host="0.0.0.0", port=50000)
