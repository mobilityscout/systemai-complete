from .registry import register

def handler():
    return {"module":"billing","status":"ok"}

register("/billing", handler)
