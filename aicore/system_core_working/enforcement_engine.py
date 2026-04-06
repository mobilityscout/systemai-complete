class EnforcementEngine:

    def enforce(self, module, issues):

        if not issues:
            return {"action": "OK"}

        # 🔴 harte Entscheidungen
        if "invalid_syntax" in issues:
            return {"action": "REBUILD"}

        if "missing_run" in issues:
            return {"action": "REBUILD"}

        if "runtime_failure" in issues:
            return {"action": "FIX"}

        return {"action": "IGNORE"}
