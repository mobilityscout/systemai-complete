def plan(goal):
    print("[PLANNER] planning for:", goal)

    steps = []

    if "api" in goal:
        steps = [
            {"type": "build", "target": "workspace/api.py"},
            {"type": "build", "target": "workspace/router.py"},
            {"type": "build", "target": "workspace/handler.py"},
        ]

    elif "system" in goal:
        steps = [
            {"type": "build", "target": "workspace/module_a.py"},
            {"type": "build", "target": "workspace/module_b.py"},
        ]

    else:
        steps = [
            {"type": "build", "target": "workspace/module.py"}
        ]

    return steps
