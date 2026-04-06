import os
import json
class StateCore:
def __init__(self, base_path):
self.base_path = base_path
self.state = {}
def save(self):
with open(os.path.join(self.base_path, "cognitive_state.json"), "w") as f:
json.dump(self.state, f, indent=2)
}
# ============================================
# EXECUTION INTROSPECTION (FIXED CLEAN)
# ============================================
import inspect
executed = False
try:
for name, obj in inspect.getmembers(mod):
if inspect.isfunction(obj):
try:
result = obj(self.state)
self.state["action_result"] = {
"action": name,
"target": module_name,
"result": result
}
executed = True
break
except Exception:
continue
except Exception as e:
self.state["action_result"] = {
"action": "error",
"target": module_name,
"error": str(e)
}
if not executed:
self.state["action_result"] = {
"action": "none",
"target": module_name,
"error": "no_callable_found"
}
