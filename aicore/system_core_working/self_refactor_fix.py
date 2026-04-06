import os

BASE = "/root/aicore"

def resolve_path(f):

    if os.path.exists(f):
        return f

    full = os.path.join(BASE, f)
    if os.path.exists(full):
        return full

    for root, dirs, files in os.walk(BASE):
        if os.path.basename(f) in files:
            return os.path.join(root, os.path.basename(f))

    return None


def already_processed(path, action_type):

    try:
        fp = resolve_path(path)
        if not fp:
            return False

        with open(fp, "r") as f:
            content = f.read()

        if action_type == "add_logging":
            return "[LOG]" in content

        if action_type == "add_try_wrapper":
            return "try:" in content and "except" in content

        return False

    except Exception:
        return False
