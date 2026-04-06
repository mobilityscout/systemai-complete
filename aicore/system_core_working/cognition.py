class Cognition:

    def analyze_cycle(self, inspect, state):

        report = {
            "health_score": 100,
            "issues": [],
            "risks": [],
            "opportunities": [],
            "summary": ""
        }

        issues = inspect.get("report", [])

        # -------------------------
        # HEALTH SCORE
        # -------------------------
        score = 100

        for i in issues:
            if i.get("decision") in ["REBUILD", "FIX"]:
                score -= 20
                report["issues"].append(i["file"])

        report["health_score"] = max(score, 0)

        # -------------------------
        # RISKS
        # -------------------------
        if score < 60:
            report["risks"].append("system_instability")

        if len(issues) > 5:
            report["risks"].append("high_issue_density")

        # -------------------------
        # OPPORTUNITIES
        # -------------------------
        for i in issues:
            if "upgrade" in i:
                report["opportunities"].append({
                    "file": i["file"],
                    "upgrade": i["upgrade"]
                })

        # -------------------------
        # SUMMARY
        # -------------------------
        if score > 80:
            report["summary"] = "system stable"
        elif score > 50:
            report["summary"] = "system degraded"
        else:
            report["summary"] = "system critical"

        return report
