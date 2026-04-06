import os
import json
import hashlib


class StateCore:

    def __init__(self, tenant_id):
        self.base = f"/root/aicore/tenants/{tenant_id}"
        self.modules = os.path.join(self.base, "modules")
        self.state_file = os.path.join(self.base, "state.json")

        os.makedirs(self.modules, exist_ok=True)

        if not os.path.exists(self.state_file):
            self._save({})

    # =========================
    # LOAD / SAVE
    # =========================

    def _load(self):
        return json.load(open(self.state_file))

    def _save(self, data):
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    # =========================
    # HASH (TRUTH)
    # =========================

    def _hash(self, path):
        try:
            data = open(path, "rb").read()
            return hashlib.sha256(data).hexdigest()
        except:
            return None

    # =========================
    # SYNC (CORE)
    # =========================

    def sync(self):

        state = self._load()
        files = os.listdir(self.modules)

        actions = []

        # -----------------------
        # FILE → STATE
        # -----------------------

        for f in files:

            if not f.endswith(".py"):
                continue

            path = os.path.join(self.modules, f)
            h = self._hash(path)

            if f not in state:
                state[f] = {
                    "version": 1,
                    "hash": h
                }
                actions.append({"register": f})

            else:
                if state[f]["hash"] != h:
                    state[f]["version"] += 1
                    state[f]["hash"] = h
                    actions.append({"update": f})

        # -----------------------
        # STATE → FILE
        # -----------------------

        for f in list(state.keys()):

            path = os.path.join(self.modules, f)

            if not os.path.exists(path):
                del state[f]
                actions.append({"remove": f})

        self._save(state)

        return actions

    # =========================
    # VERIFY (PROTECTION)
    # =========================

    def verify(self):

        state = self._load()
        issues = []

        for f, meta in state.items():

            path = os.path.join(self.modules, f)

            if not os.path.exists(path):
                issues.append({"file": f, "issue": "missing_file"})
                continue

            current_hash = self._hash(path)

            if current_hash != meta["hash"]:
                issues.append({"file": f, "issue": "tampered"})

        return issues
