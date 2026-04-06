class AdaptationCore:

    def __init__(self):
        self.memory = []

    # =========================
    # LEARN FROM CYCLE
    # =========================

    def learn(self, cognition, experiment):

        entry = {
            "health": cognition.get("health_score"),
            "issues": cognition.get("issues", []),
            "summary": cognition.get("summary"),
            "experiment": experiment
        }

        self.memory.append(entry)

        if len(self.memory) > 100:
            self.memory.pop(0)

    # =========================
    # CAUSAL ANALYSIS
    # =========================

    def detect_patterns(self):

        patterns = []

        for i in range(1, len(self.memory)):

            prev = self.memory[i - 1]
            curr = self.memory[i]

            # 🔴 Experiment → Degradation
            if prev.get("experiment") and curr["health"] < prev["health"]:
                patterns.append({
                    "type": "experiment_caused_failure",
                    "target": prev["experiment"]["target"]
                })

            # 🔴 Failure → Recovery
            if prev["health"] < 100 and curr["health"] == 100:
                patterns.append({
                    "type": "recovery_success"
                })

        return patterns

    # =========================
    # SYSTEM IMPROVEMENT
    # =========================

    def propose_system_actions(self, patterns):

        actions = []

        for p in patterns:

            if p["type"] == "experiment_caused_failure":
                actions.append({
                    "type": "strengthen_validation",
                    "target": p["target"]
                })

            if p["type"] == "recovery_success":
                actions.append({
                    "type": "optimize_repair_strategy"
                })

        return actions
