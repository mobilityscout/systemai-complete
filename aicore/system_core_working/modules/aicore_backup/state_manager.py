import json
import os


class StateManager:
    """
    Tenant-gebundener Registry-State.
    """

    def __init__(self, tenant_id: str):
        self.path = f"/root/aicore/tenants/{tenant_id}/state/registry.json"
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def get_registry(self) -> dict:
        with open(self.path, "r") as f:
            return json.load(f)

    def set_registry(self, data: dict) -> None:
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)
