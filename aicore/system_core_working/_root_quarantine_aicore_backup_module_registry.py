from aicore.state_manager import StateManager


class ModuleRegistry:
    """
    Einfache Modulversionierung pro Tenant.
    """

    def __init__(self, tenant_id: str):
        self.state = StateManager(tenant_id)

    def register(self, name: str) -> dict:
        data = self.state.get_registry()

        if name not in data:
            data[name] = {
                "version": 1,
                "status": "active"
            }
        else:
            data[name]["version"] += 1
            data[name]["status"] = "active"

        self.state.set_registry(data)
        return data[name]
