import os


class HealthMonitor:
    """
    Filesystem-basierter Health-Check.
    Kein Registry-Zwang.
    """

    def __init__(self, tenant_id: str):
        self.base = f"/root/aicore/tenants/{tenant_id}/modules"
        os.makedirs(self.base, exist_ok=True)

    def scan(self) -> list[dict]:
        results = []

        for filename in os.listdir(self.base):
            if not filename.endswith(".py"):
                continue

            module = filename[:-3]
            path = os.path.join(self.base, filename)

            results.append({
                "module": module,
                "path": path,
                "health": self._check_python(path),
            })

        return results

    def _check_python(self, path: str) -> dict:
        try:
            with open(path, "r") as f:
                code = f.read()

            compile(code, path, "exec")

            if "def run" not in code:
                return {
                    "status": "fail",
                    "reason": "missing run() function"
                }

            namespace = {}
            exec(code, namespace)

            if "run" not in namespace:
                return {
                    "status": "fail",
                    "reason": "run() not defined"
                }

            namespace["run"]()

            return {"status": "ok"}

        except Exception as e:
            return {
                "status": "fail",
                "reason": f"execution error: {e}"
            }
