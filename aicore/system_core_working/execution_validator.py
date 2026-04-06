class ExecutionValidator:

    def validate(self, payload: str):

        forbidden = [
            "rm -rf",
            "shutdown",
            "reboot",
            ":(){ :|:& };:"
        ]

        for f in forbidden:
            if f in payload:
                raise Exception(f"FORBIDDEN COMMAND: {f}")

        return True
