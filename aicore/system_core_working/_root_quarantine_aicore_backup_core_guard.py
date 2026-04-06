import os


class CoreGuard:
    """
    Minimaler Dateiguard für den Basiskern.
    """

    def validate_file(self, path: str) -> dict:
        if not os.path.exists(path):
            return {
                "status": "fail",
                "reason": "file missing"
            }

        return {"status": "ok"}
