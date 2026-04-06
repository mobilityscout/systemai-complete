import py_compile
import os


class CoreHealth:

    CORE_FILES = [
        "ai_manager.py",
        "executor.py",
        "write_guard.py",
        "health_monitor.py"
    ]

    BASE = "/root/aicore"

    def scan(self):

        issues = []

        for f in self.CORE_FILES:

            path = os.path.join(self.BASE, f)

            try:
                py_compile.compile(path, doraise=True)
            except Exception as e:
                issues.append({
                    "file": f,
                    "type": "syntax_error",
                    "error": str(e)
                })

        return issues
