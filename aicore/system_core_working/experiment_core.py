import os
import random


class ExperimentCore:

    def __init__(self, base):
        self.base = base

    def inject(self):

        files = [f for f in os.listdir(self.base) if f.endswith(".py")]

        if not files:
            return None

        target = random.choice(files)
        path = os.path.join(self.base, target)

        try:
            with open(path, "w") as f:
                f.write("BROKEN")
            return {"experiment": "break", "target": target}
        except:
            return None
