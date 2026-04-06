import time
import hashlib
import os

from aicore.health_monitor import HealthMonitor
from aicore.auto_repair import AutoRepair


class ImmuneDaemon:

    def __init__(self, tenant_id, interval=2):
        self.monitor = HealthMonitor(tenant_id)
        self.repair = AutoRepair(tenant_id)
        self.interval = interval
        self.hashes = {}

    def _hash(self, path):

        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def run(self):

        print("IMMUNE V2 ACTIVE")

        while True:

            results = self.monitor.scan()

            for r in results:

                module = r["module"]
                path = r["path"]
                health = r["health"]

                current_hash = self._hash(path)
                last_hash = self.hashes.get(module)

                if current_hash == last_hash:
                    continue

                self.hashes[module] = current_hash

                if health["status"] == "fail":

                    print(f"[FAIL] {module} → {health}")

                    result = self.repair.fix(module)

                    print(f"[FIXED] {module} → {result}")

            time.sleep(self.interval)
