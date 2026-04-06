from .router import route
from .loader import load_all

# lädt alle Module
load_all()

def handle(path):
    return route(path)
