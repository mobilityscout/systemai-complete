import os

class WorldState:
    def __init__(self, base_path):
        self.base_path = base_path
        self.paths = {}
        self.missing = []
        self.valid = []
        self.summary = {}

    def scan(self):
        targets = [
            "knowledge",
            "knowledge/reality",
            "knowledge/improvements",
            "knowledge/decisions",
            "memory.json",
            "graph.json"
        ]

        for t in targets:
            full = os.path.join(self.base_path, t)
            exists = os.path.exists(full)

            self.paths[t] = {
                "path": full,
                "exists": exists
            }

            if exists:
                self.valid.append(t)
            else:
                self.missing.append(t)

        self.summary = {
            "valid": len(self.valid),
            "missing": len(self.missing),
            "total": len(targets)
        }

        return self

    def is_world_valid(self):
        return len(self.missing) == 0

