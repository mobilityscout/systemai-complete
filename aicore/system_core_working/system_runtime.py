import time
from aicore.system_entry import SystemEntry
from aicore.cognition import Cognition
from aicore.adaptation_core import AdaptationCore
from aicore.experiment_core import ExperimentCore
from aicore.forensic_core import ForensicCore


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

    def evaluate(self):

        if len(self.history) < 2:
            return {}

        prev = self.history[-2]["health"]
        curr = self.history[-1]["health"]

        trend = "stable"
        if curr > prev:
            trend = "improving"
        elif curr < prev:
            trend = "degrading"

        last = self.history[-10:]
        stable = sum(1 for h in last if h["health"] == 100)

        stability_rate = stable / len(last)

        return {
            "trend": trend,
            "stability_rate": stability_rate
        }

    def decide(self, analysis):

        actions = []

        rate = analysis.get("stability_rate", 0)

        if rate > 0.8:
            actions.append({
                "type": "increase_autonomy",
                "confidence": "high",
                "reason": f"stability_rate={rate}"
            })

        elif rate < 0.5:
            actions.append({
                "type": "reduce_experiments",
                "confidence": "high",
                "reason": f"stability_rate={rate}"
            })

        return actions


class SystemRuntime:

    def __init__(self, tenant_id="t1", interval=2):
        self.system = SystemEntry(tenant_id)
        self.cognition = Cognition()
        self.adaptation = AdaptationCore()
        self.forensic = ForensicCore()
        self.analytical = AnalyticalCore()
        self.experiment = ExperimentCore(f"/root/aicore/tenants/{tenant_id}/modules")

        self.interval = interval
        self.tick = 0

    def run(self):

        print("COGNITIVE SYSTEM (FINAL ANALYTICAL MODE)")

        while True:

            try:
                self.tick += 1

                # CONTROLLED EXPERIMENT
                exp = None
                if self.tick % 5 == 0:
                    exp = self.experiment.inject()

                inspect = self.system.handle("inspect")
                state = self.system.handle("state")

                cognition = self.cognition.analyze_cycle(inspect, state)

                forensics = self.forensic.analyze(inspect, exp)

                self.adaptation.learn(cognition, exp)
                patterns = self.adaptation.detect_patterns()

                self.analytical.record(cognition)
                analysis = self.analytical.evaluate()
                decisions = self.analytical.decide(analysis)

                print({
                    "cycle": {
                        "health": cognition["health_score"],
                        "summary": cognition["summary"],
                        "forensics": forensics,
                        "patterns": patterns,
                        "analysis": analysis,
                        "decisions": decisions
                    }
                })

            except Exception as e:
                print({"runtime_error": str(e)})

            time.sleep(self.interval)
