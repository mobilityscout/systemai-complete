class PolicyEngine:
    """
    Zentrale Systemregeln (nicht verhandelbar)
    """

    def evaluate(self, module):

        issues = []

        # 🔴 RULE 1: python muss run() haben
        if module["type"] == "backend":
            if module["analysis"]["contract"] != "ok":
                issues.append("missing_run")

        # 🔴 RULE 2: syntax muss valide sein
        if module["analysis"]["syntax"] != "ok":
            issues.append("invalid_syntax")

        # 🔴 RULE 3: runtime muss laufen
        if module["analysis"]["runtime"] != "ok":
            issues.append("runtime_failure")

        return issues
