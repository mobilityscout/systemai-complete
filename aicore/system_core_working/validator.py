class Validator:
    """
    Minimaler Safety-Layer für den Basiskern.
    """

    BLOCKED_TOKENS = ["rm", "shutdown", "reboot", "mkfs", "dd"]

    def validate(self, wp: dict) -> dict:
        target = wp.get("target", "")

        for token in self.BLOCKED_TOKENS:
            if token in target:
                return {
                    "status": "blocked",
                    "reason": f"blocked token detected: {token}"
                }

        if not wp.get("actions"):
            return {
                "status": "blocked",
                "reason": "no actions"
            }

        return {"status": "ok"}
