import os

BASE = "/root/aicore/workspace"

def evaluate():
    files = ["api.py", "router.py", "handler.py"]

    existing = [os.path.exists(os.path.join(BASE, f)) for f in files]

    # 🔴 nichts vorhanden → build
    if not any(existing):
        return "build api system"

    # 🔴 teilweise vorhanden → rebuild
    if not all(existing):
        return "rebuild api system"

    # 🔴 einfache Fehlerprüfung (Syntax)
    for f in files:
        path = os.path.join(BASE, f)
        try:
            compile(open(path).read(), path, 'exec')
        except:
            return "rebuild api system"

    return "maintain system"
