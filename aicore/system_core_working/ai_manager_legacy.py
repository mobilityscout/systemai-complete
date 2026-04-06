from world_perception import WorldState
from world_guard import WorldGuard
import os
import os
import time
import json

class AIManager:

    def __init__(self, tenant_id=None):
        self.tenant_id = tenant_id
        self.base = os.getcwd() + "/aicore/knowledge"

        self.state = {
            "mode": "STABLE",
            "history": []
        }

    # =========================
    # WRITE TO PRINCIPLE
    # =========================

    def _store(self, space, data):
        path = os.path.join(self.base, space, str(int(time.time())) + ".json")
        with open(path, "w") as f:
            json.dump(data, f)

    # =========================
    # REALITY
    # =========================

    def _reality(self):
        return {
            "status": "running",
            "mode": self.state["mode"]
        }

    # =========================
    # ANALYSIS
    # =========================

    def _analyze(self):
        improvements = [
            "add_logging",
            "add_error_handling"
        ]

        opportunities = [
            "performance_optimization",
            "module_standardization"
        ]

        return improvements, opportunities

    # =========================
    # EVOLUTION DECISION
    # =========================

    def _decide(self, improvements, opportunities):
        decisions = []

        if improvements:
            decisions.append("IMPROVE_SYSTEM")

        if opportunities:
            decisions.append("EXPAND_CAPABILITIES")

        return decisions

    # =========================
    # STABILITY
    # =========================

    def _stability(self):
        self.state["history"].append(1)
        if len(self.state["history"]) > 10:
            self.state["history"].pop(0)

        rate = sum(self.state["history"]) / len(self.state["history"])

        if rate > 0.8:
            self.state["mode"] = "HIGH_AUTONOMY"

        return rate

    # =========================
    # COGNITIVE LOOP
    # =========================

    def _cycle(self):

        reality = self._reality()

        improvements, opportunities = self._analyze()

        decisions = self._decide(improvements, opportunities)

        stability = self._stability()

        # 🔴 STORE IN PRINCIPLE BRAIN

        self._store("reality", reality)
        self._store("improvements", improvements)
        self._store("opportunities", opportunities)
        self._store("decisions", decisions)

        return {
            "state": reality,
            "decisions": decisions,
            "stability": stability
        }

    # =========================
    # ENTRY
    # =========================

    def handle(self, input_data):
        base_path = os.path.dirname(os.path.abspath(__file__))
        world = WorldState(base_path).scan()
        guard = WorldGuard(world)

        if not guard.can_write():
            return {"status": "WORLD_INVALID", "details": guard.report()}

        result = self._cycle()

        return {
            "status": "executed",
            "cognitive": result,
            "input": input_data
        }
