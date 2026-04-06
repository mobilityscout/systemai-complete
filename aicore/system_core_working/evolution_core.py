class EvolutionCore:
    """
    Bewertet Module auf Verbesserungen (nicht nur Fehler)
    """

    def evaluate(self, module, analysis):

        suggestions = []

        # 🔴 BASIC STANDARD
        if analysis["contract"] != "ok":
            return suggestions

        # 🔴 CHECK CONTENT
        try:
            code = open(module).read()
        except:
            return suggestions

        # 🔴 LOGGING FEHLT
        if "print(" not in code:
            suggestions.append("add_logging")

        # 🔴 ERROR HANDLING FEHLT
        if "try:" not in code:
            suggestions.append("add_error_handling")

        # 🔴 RETURN STANDARD
        if "return" not in code:
            suggestions.append("add_return")

        return suggestions
