import json
import os
import planner_engine
import dependency_engine
import autonomy_engine

GOAL = "/root/aicore/goal.json"
TODO = "/root/aicore/todo.json"
BASE = "/root/aicore/workspace"

def load(path, default):
    try:
        return json.load(open(path))
    except:
        return default

def save(path, data):
    json.dump(data, open(path, "w"), indent=2)

def get_goal():
    try:
        return json.load(open(GOAL)).get("goal", "")
    except:
        return ""

def goal_done(goal):
    if "rebuild" in goal:
        return False

    if "api" in goal:
        required = ["api.py", "router.py", "handler.py"]
        return all(os.path.exists(os.path.join(BASE, f)) for f in required)

    return False

def run():
    print("[AI MANAGER AUTONOMOUS]")

    tasks = load(TODO, [])
    goal = get_goal()

    # 🔥 AUTONOMY FIRST
    auto_goal = autonomy_engine.evaluate()
    if auto_goal != goal:
        print("[AI][AUTO] overriding goal →", auto_goal)
        goal = auto_goal
        json.dump({"goal": goal}, open(GOAL, "w"))

    # 🔴 MAINTAIN MODE
    if "maintain" in goal:
        print("[AI] maintain mode → idle")
        return

    # 🔴 laufende tasks
    if tasks:
        print("[AI] executing plan...")
        return

    # 🔴 goal erreicht
    if goal_done(goal):
        print("[AI] goal achieved → idle")
        return

    # 🔴 PLAN
    print("[AI] creating plan")

    plan = dependency_engine.build_plan(goal)
    if not plan:
        plan = planner_engine.plan(goal)

    save(TODO, plan)

    # 🔴 rebuild → zurück zu maintain
    if "rebuild" in goal:
        print("[AI] rebuild done → switching to maintain")
        json.dump({"goal": "maintain system"}, open(GOAL, "w"))
