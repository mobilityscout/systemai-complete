from aicore.deploy_pipeline import DeployPipeline
from aicore.health_monitor import HealthMonitor
from aicore.auto_repair import AutoRepair


class AIManager:

    def __init__(self, tenant_id="t1"):
        self.tenant_id = tenant_id
        self.deploy = DeployPipeline()
        self.monitor = HealthMonitor(tenant_id)
        self.repair = AutoRepair(tenant_id)

    # 🔴 EINZIGER ENTRY
    def handle_chat(self, raw):

        text = (raw or "").strip().lower()

        parts = text.split()

        if not parts:
            return {"status": "empty"}

        cmd = parts[0]

        if cmd == "build" and len(parts) >= 2:
            return self._build(parts[1])

        if cmd == "fix" and len(parts) >= 2:
            return self._fix(parts[1])

        if cmd == "status":
            return self._status()

        return {
            "status": "rejected",
            "input": text
        }

    # 🔴 COMMANDS

    def _build(self, target):

        wp = {
            "tenant_id": self.tenant_id,
            "intent": "BUILD",
            "target": target,
            "actions": [{"type": "WRITE_CODE"}]
        }

        return self.deploy.run(wp)

    def _fix(self, target):

        return self.repair.fix(target)

    def _status(self):

        return self.monitor.scan()

    # 🔴 IMMUNE LOOP
    def tick(self):

        events = []

        for r in self.monitor.scan():

            if r["health"]["status"] == "fail":

                fix = self.repair.fix(r["module"])

                events.append({
                    "module": r["module"],
                    "fix": fix
                })

        return events
