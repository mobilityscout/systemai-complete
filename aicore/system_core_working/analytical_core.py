class AnalyticalCore:

    def __init__(self):
        self.history = []

    def record(self, cognition):
        entry = {
            "health": cognition.get("health_score")
        }
        self.history.append(entry)

        if len(self.history) > 50:
            self.history.pop(0)

    def compare(self):

        if len(self.history) < 2:
            return {}

        prev = self.history[-2]["health"]
        curr = self.history[-1]["health"]

        result = {}

        if curr > prev:
            result["trend"] = "improving"
        elif curr < prev:
            result["trend"] = "degrading"
        else:
            result["trend"] = "stable"

        # 🔴 STABILITY RATE (NEU!)
        last = self.history[-10:]
        stable = sum(1 for h in last if h["health"] == 100)

        result["stability_rate"] = stable / len(last)

        return result

    def compress_patterns(self, patterns):

        summary = {}

        for p in patterns:
            t = p["type"]
            summary[t] = summary.get(t, 0) + 1

        return [{"type": k, "count": v} for k, v in summary.items()]

    def propose(self, compressed, analysis):

        actions = []

        rate = analysis.get("stability_rate", 0)

        # 🔴 ENTSCHEIDUNG AUF BASIS DER RATE
        if rate > 0.8:
            actions.append({
                "type": "increase_autonomy",
                "confidence": "high",
                "reason": f"stability_rate={rate}"
            })

        if rate < 0.5:
            actions.append({
                "type": "reduce_experiments",
                "confidence": "high",
                "reason": "system unstable"
            })

        return actions
