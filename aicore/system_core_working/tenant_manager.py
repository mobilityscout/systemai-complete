import os


class TenantManager:

    BASE = "aicore/tenants"

    def ensure(self, tenant_id):

        base = os.path.join(self.BASE, tenant_id)

        paths = {
            "base": base,
            "modules": os.path.join(base, "modules"),
            "state": os.path.join(base, "state"),
            "versions": os.path.join(base, "versions"),
        }

        for p in paths.values():
            os.makedirs(p, exist_ok=True)

        # init state files
        self._init_file(paths["state"], "queue.json", "[]")
        self._init_file(paths["state"], "registry.json", "{}")

        return paths

    def _init_file(self, base, name, default):

        path = os.path.join(base, name)

        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(default)
