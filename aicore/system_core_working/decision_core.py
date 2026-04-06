class DecisionCore:
    """
    Deterministische Entscheidungsengine (v2)
    """

    def evaluate(self, analysis):

        score = 100
        reasons = []

        # 🔴 SYNTAX
        if analysis["syntax"] != "ok":
            score -= 70
            reasons.append("syntax_fail")

        # 🔴 CONTRACT
        if analysis["contract"] != "ok":
            score -= 20
            reasons.append("contract_fail")

        # 🔴 RUNTIME
        if analysis["runtime"] != "ok":
            score -= 30
            reasons.append("runtime_fail")

        # 🔴 DECISION LOGIC
        if score <= 30:
            action = "REBUILD"
        elif score <= 70:
            action = "FIX"
        else:
            action = "OK"

        return {
            "score": score,
            "action": action,
            "reasons": reasons,
            "confidence": self._confidence(score)
        }

    def _confidence(self, score):

        if score > 80:
            return 1.0
        if score > 60:
            return 0.8
        if score > 40:
            return 0.6
        return 0.3
