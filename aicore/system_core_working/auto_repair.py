from aicore.executor import WorkPackageExecutor


class AutoRepair:
    """
    Deterministische Reparatur über denselben Executor wie Deploy.
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.executor = WorkPackageExecutor(tenant_id)

    def fix(self, module: str) -> dict:
        wp = {
            "tenant_id": self.tenant_id,
            "intent": "FIX",
            "target": module,
            "actions": [{"type": "WRITE_CODE"}]
        }

        return self.executor.execute(wp)
