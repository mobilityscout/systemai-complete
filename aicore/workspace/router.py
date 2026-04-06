from .registry import get

def route(path):
    handler = get(path)
    return handler()
