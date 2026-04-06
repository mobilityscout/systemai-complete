import os


class SystemWatch:
    """
    Systemweite Compliance- und Strukturprüfung
    """

    REQUIRED_STRUCTURE = [
        "tenants",
        "tenants/t1/modules",
        "tenants/t1/state"
    ]

    REQUIRED_PATTERNS = {
        ".py": "def run"
    }

    def __init__(self, base="/root/aicore"):
        self.base = base

    def scan(self):

        issues = []

        # 🔴 Struktur prüfen
        for path in self.REQUIRED_STRUCTURE:
            full = os.path.join(self.base, path)

            if not os.path.exists(full):
                issues.append({
                    "type": "structure",
                    "path": full,
                    "issue": "missing"
                })

        # 🔴 Module prüfen
        modules_path = os.path.join(self.base, "tenants/t1/modules")

        if os.path.exists(modules_path):
            for f in os.listdir(modules_path):

                full = os.path.join(modules_path, f)

                if f.endswith(".py"):
                    code = open(full).read()

                    if "def run" not in code:
                        issues.append({
                            "type": "code",
                            "file": full,
                            "issue": "missing run()"
                        })

        return issues
