class ForensicCore:

    def analyze(self, inspect, experiment):

        findings = []

        for item in inspect.get("report", []):

            if item.get("decision") in ["REBUILD", "FIX"]:

                findings.append({
                    "file": item["file"],
                    "failure_type": item["decision"],
                    "analysis": item.get("analysis"),
                    "trigger": experiment,
                    "impact": self._impact(item),
                    "phase": self._phase(item)
                })

        return findings

    def _impact(self, item):

        a = item.get("analysis", {})

        if a.get("contract") != "ok":
            return "contract_failure"

        if a.get("runtime") != "ok":
            return "runtime_failure"

        if a.get("syntax") != "ok":
            return "syntax_failure"

        return "unknown"

    def _phase(self, item):

        a = item.get("analysis", {})

        if a.get("syntax") != "ok":
            return "compile"

        if a.get("contract") != "ok":
            return "load"

        if a.get("runtime") != "ok":
            return "execute"

        return "unknown"
