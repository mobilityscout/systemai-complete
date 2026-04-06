from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

class SafeAI:
    def handle(self, msg):
        try:
            from aicore.ai_manager import AIManager
            ai = AIManager("t1")
            return ai.handle(msg)
        except Exception as e:
            return {
                "error": "AI_MANAGER_FAIL",
                "details": str(e),
                "trace": traceback.format_exc()
            }

ai = SafeAI()

@app.route("/")
def index():
    return "AI Manager UI running"

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    msg = data.get("message", "")
    return jsonify(ai.handle(msg))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=50000)
