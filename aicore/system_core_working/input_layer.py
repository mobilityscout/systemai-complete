class InputLayer:
    """
    Klassifiziert Eingaben deterministisch.
    """

    def process(self, raw):

        text = (raw or "").strip()

        # 🔴 PROMPT CLEAN
        while text.startswith(">>"):
            text = text[2:].strip()

        # 🔴 LEER
        if not text:
            return {"type": "EMPTY"}

        # 🔴 SHELL COMMAND
        if text.startswith("!"):
            return {
                "type": "SHELL",
                "command": text[1:].strip()
            }

        # 🔴 NOISE (Terminal Copy)
        if "root@" in text or "EOF" in text:
            return {
                "type": "NOISE",
                "raw": text
            }

        # 🔴 STANDARD COMMAND
        parts = text.split()

        return {
            "type": "COMMAND",
            "cmd": parts[0].lower(),
            "args": parts[1:]
        }
