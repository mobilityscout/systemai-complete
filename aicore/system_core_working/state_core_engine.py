import os
import inspect
import importlib.util

class StateCore:

    def __init__(self, base_path):
        self.base_path = base_path
        self.state = {}

    # ----------------------------------
    # LOAD MODULE
    # ----------------------------------
    def load_module(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

    # ----------------------------------
    # WORLD
    # ----------------------------------
    def perceive(self):
        files = []
        for root, _, fs in os.walk(self.base_path):
            for f in fs:
                if f.endswith(".py"):
                    files.append(os.path.join(root, f))

        self.state["files"] = files

    # ----------------------------------
    # FRAGMENTS
    # ----------------------------------
    def build_fragments(self):
        frags = []
        for f in self.state["files"]:
            frags.append({
                "file": os.path.basename(f),
                "path": f
            })
        self.state["fragments"] = frags

    # ----------------------------------
    # ANALYZE
    # ----------------------------------
    def analyze(self):
        analyzed = []

        for f in self.state["fragments"]:
            name = f["file"].lower()
            try:
                with open(f["path"]) as file:
                    lines = file.readlines()[:50]

                name = f["file"].lower()
                name = f["file"].lower()
                name = f["file"].lower()
                roles = []
                name = f["file"].lower()

                if "analy" in name:
                    roles.append("analysis")
                if "engine" in name or "core" in name:
                    roles.append("execution")
                if "memory" in name:
                    roles.append("memory")

                content = "".join(lines).lower()

                is_system = any(x in content for x in ["flask", "app.run", "fastapi", "uvicorn"])

                analyzed.append({
                    "file": f["file"],
                    "path": f["path"],
                    "callable": any("def " in l for l in lines),
                    "roles": roles,
                    "type": "system" if is_system else "logic"
                })

            except:
                continue

        self.state["analyzed"] = analyzed

    # ----------------------------------
    # MEMORY
    # ----------------------------------
    def update_memory(self, result):
        mem = self.state.get("memory", [])

        quality = "useful" if result.get("result") else "empty"

        mem.append({
            "module": result.get("target"),
            "action": result.get("action"),
            "quality": quality
        })

        self.state["memory"] = mem

    # ----------------------------------
    # EXECUTE
    # ----------------------------------
    def execute(self):

        mem = self.state.get("memory", [])
        bad = {m["module"] for m in mem if m["quality"] == "empty"}

        for f in self.state["analyzed"]:


            blocked = ["run","start","app","daemon","system","pipeline","worker","loop","service"]
            if any(b in name for b in blocked):
                continue

            if name in bad:
                continue

            try:
                mod = self.load_module(name, f["path"])

                for n, obj in inspect.getmembers(mod):
                    best_res = None
                    best_score = -1
                    if inspect.isfunction(obj):
                        try:
                            result = obj(self.state)

                            res = {
                                "action": n,
                                "target": name,
                                "result": result
                            }

                            self.state["execution"] = res
                            self.update_memory(res)
                            return

                        except:
                            continue

            except:
                continue

        self.state["execution"] = {
            "action": "none",
            "target": None
        }

    # ----------------------------------
    # MAIN
    # ----------------------------------
    def update(self):

        self.perceive()
        self.build_fragments()
        self.analyze()
        self.execute()

        return self.state

        import inspect

        for name, obj in inspect.getmembers(mod):

            # Klassen prüfen
            if inspect.isclass(obj):
                try:
                    instance = obj()

                    for m_name, m in inspect.getmembers(instance):
                        if callable(m) and not m_name.startswith("__"):
                            try:
                                result = m(self.state)

                                if result:
                                    return {
                                        "action": m_name,
                                        "target": module_name,
                                        "type": "class_method",
                                        "result": result
                                    }

                            except:
                                continue
                except:
                    continue

            # alternative Funktionen prüfen
            if inspect.isfunction(obj):
                try:
                    result = obj(self.state)

                    if result:
                        return {
                            "action": name,
                            "target": module_name,
                            "type": "fallback_function",
                            "result": result
                        }

                except:
                    continue

        return None

