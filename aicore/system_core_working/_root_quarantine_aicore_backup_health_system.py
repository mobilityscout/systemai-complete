import os


class HealthSystem:

    def __init__(self, tenant_id):
        self.base = f"aicore/tenants/{tenant_id}/modules"

    def validate(self, wp):

        type_ = wp["type"]
        name = wp["target"]

        if type_ == "backend":
            return self._check_python(name)

        return {"status": "ok"}

    def _check_python(self, name):

        path = f"{self.base}/{name}.py"

        if not os.path.exists(path):
            return {"status": "fail", "reason": "missing python"}

        try:
            code = open(path).read()

            # 🔴 1. Syntax
            compile(code, path, 'exec')

            # 🔴 2. Struktur prüfen
            if "def run" not in code:
                return {"status": "fail", "reason": "missing run() function"}

            # 🔴 3. Execution Test (optional aber stark)
            namespace = {}
            exec(code, namespace)

            if "run" not in namespace:
                return {"status": "fail", "reason": "run() not defined"}

            # Test call
            namespace["run"]()

            return {"status": "ok"}

        except Exception as e:
            return {"status": "fail", "reason": f"execution error: {e}"}
