class DecisionCore:
    """
    Zentrale Entscheidungsinstanz.
    Keine Logik außerhalb davon erlaubt.
    """

    def evaluate(self, analysis):

        # 🔴 harte Invarianten (nicht verhandelbar)
        if analysis["syntax"] == "fail":
            return "REBUILD"

        if analysis["contract"] != "ok":
            return "REBUILD"

        if analysis["runtime"] == "fail":
            return "FIX"

        return "OK"
