import json

def decide(module):

    if module["completion"] == 100 and module["classes"] > 10:
        return {
            "decision": "promote_to_core",
            "reason": "fully structured and complete system"
        }

    if module["completion"] > 60:
        return {
            "decision": "improve",
            "reason": "usable but incomplete"
        }

    return {
        "decision": "ignore",
        "reason": "low value"
    }

if __name__ == "__main__":
    print("READY")
