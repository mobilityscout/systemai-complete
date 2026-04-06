class CommandParser:

    VALID = {
        "build": "BUILD",
        "fix": "FIX",
        "status": "STATUS",
        "system": "SYSTEM",
        "inspect": "INSPECT"
    }

    def parse(self, text):

        parts = text.strip().split()

        if not parts:
            return {"type": "UNKNOWN"}

        cmd = parts[0].lower()

        if cmd in self.VALID:
            return {
                "type": self.VALID[cmd],
                "target": parts[1] if len(parts) > 1 else None
            }

        return {"type": "UNKNOWN"}
