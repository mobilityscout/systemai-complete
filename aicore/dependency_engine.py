def build_plan(goal):
    print("[DEPS] building dependency plan for:", goal)

    if "api" in goal:
        return [
            {
                "type": "build",
                "target": "workspace/handler.py",
                "code": """def handle():
    return {"message": "ok"}"""
            },
            {
                "type": "build",
                "target": "workspace/router.py",
                "code": """from handler import handle

def route():
    return handle()"""
            },
            {
                "type": "build",
                "target": "workspace/api.py",
                "code": """from router import route

def run():
    print(route())

if __name__ == "__main__":
    run()"""
            }
        ]

    return []
