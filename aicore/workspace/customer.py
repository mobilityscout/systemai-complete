from .registry import register

def handler():
    return {"module":"customer","status":"ok"}

register("/customer", handler)
