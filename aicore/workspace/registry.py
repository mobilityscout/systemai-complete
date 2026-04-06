ROUTES = {}

def register(path, func):
    print("[REGISTER]", path)
    ROUTES[path] = func

def get(path):
    print("[ROUTES AVAILABLE]", list(ROUTES.keys()))
    return ROUTES.get(path, lambda: {"error":"not found"})
