class WorldGuard:

    def __init__(self, world_state):
        self.world = world_state

    def can_write(self):
        return self.world.is_world_valid()

    def report(self):
        return {
            "missing_paths": self.world.missing,
            "valid_paths": self.world.valid,
            "status": "blocked" if not self.can_write() else "ok"
        }
