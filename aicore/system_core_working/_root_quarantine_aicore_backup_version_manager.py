import os
import shutil


class VersionManager:

    BASE_PATH = "aicore/versions"

    def __init__(self):
        os.makedirs(self.BASE_PATH, exist_ok=True)

    def backup(self, path):

        if not os.path.exists(path):
            return None

        name = os.path.basename(path)
        version = self._next_version(name)

        backup_path = os.path.join(self.BASE_PATH, f"{name}_v{version}")

        shutil.copy(path, backup_path)

        return backup_path

    def restore_latest(self, path):

        name = os.path.basename(path)

        candidates = [
            f for f in os.listdir(self.BASE_PATH)
            if f.startswith(name + "_v")
        ]

        if not candidates:
            return {"status": "no_backup"}

        latest = sorted(candidates)[-1]

        src = os.path.join(self.BASE_PATH, latest)

        shutil.copy(src, path)

        return {
            "status": "restored",
            "from": latest
        }

    def _next_version(self, name):

        existing = [
            f for f in os.listdir(self.BASE_PATH)
            if f.startswith(name + "_v")
        ]

        return len(existing) + 1
