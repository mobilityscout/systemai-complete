print('[LOG] start')
import json, time

STATE = "/root/aicore/state.json"

def get_state():
    try:
        return json.load(open(STATE))
    except:
        return {"stats": {"total":0,"high_value":0}}

def decide():

    s = get_state()["stats"]

    total = s.get("total",0)
    high = s.get("high_value",0)

    # 🔴 NO PROGRESS → STOP INTEGRATION SPAM
    if high < 50:
        return {
            "perception": True,
            "attention": True,
            "thinking": False,
            "integration": False
        }

    # 🟡 ENOUGH DATA → THINK
    if high >= 50:
        return {
            "perception": False,
            "attention": True,
            "thinking": True,
            "integration": True
        }

    return {}

def run():
    return decide()

if __name__ == "__main__":
    print(json.dumps(run()))
