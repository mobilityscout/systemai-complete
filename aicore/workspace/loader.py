import os
import importlib

BASE = "/root/aicore/workspace"

def load_all():
    for file in os.listdir(BASE):
        if file.endswith(".py") and file not in ["api.py", "router.py", "registry.py", "loader.py", "__init__.py"]:
            module = file.replace(".py","")
            importlib.import_module(f"workspace.{module}")
            print("[LOADED]", module)
