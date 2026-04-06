class HealthDecisionEngine:

    def decide(self, module, health):

        status = health.get("status")
        reason = health.get("reason", "")

        # 🔴 SAFE FAILS → AUTO FIX
        if status == "fail" and "invalid html" in reason:
            return {
                "action": "repair",
                "confidence": 0.9
            }

        if status == "fail" and "syntax" in reason:
            return {
                "action": "repair",
                "confidence": 0.7
            }

        # 🔴 UNKNOWN → ESCALATE
        return {
            "action": "alert",
            "confidence": 0.3
        }
