import os
from aicore.module_registry import ModuleRegistry
from aicore.write_guard import WriteGuard


class WorkPackageExecutor:
    """
    Führt ein WorkPackage für genau einen Tenant aus.
    """

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.registry = ModuleRegistry(tenant_id)
        self.writer = WriteGuard()
        self.base = f"/root/aicore/tenants/{tenant_id}/modules"

    def execute(self, wp: dict) -> dict:
        target = os.path.basename(wp.get("target", "default")).lower()
        actions = wp.get("actions", [])

        write_result = None

        for action in actions:
            if action["type"] == "WRITE_CODE":
                write_result = self._write_python_module(target)

        version = self.registry.register(target)

        return {
            "write": write_result,
            "version": version
        }

    def _write_python_module(self, module_name: str) -> dict:
        path = os.path.join(self.base, f"{module_name}.py")

        code = f'''def run():
    return "{module_name} running"
'''

        return self.writer.safe_write(path, code)
