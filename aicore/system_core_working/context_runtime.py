import os, json

BASE = "/root/aicore"
CTX_PATH = "/root/aicore/context_memory.json"
MEM_PATH = "/root/aicore/memory.json"

def build_context(base=BASE):
    files = []
    tree = {}

    for root, dirs, fs in os.walk(base):
        rel_root = root.replace(base, "") or "/"
        tree.setdefault(rel_root, [])

        for f in fs:
            if f.endswith(".py"):
                path = os.path.join(root, f)
                files.append(path)
                tree[rel_root].append(f)

    ctx = {
        "total_files": len(files),
        "files": files,
        "structure": tree
    }
    return ctx

def save_context(ctx):
    with open(CTX_PATH, "w") as f:
        json.dump(ctx, f, indent=2)

def save_memory(ctx):
    mem = {
        "total_files": ctx.get("total_files", 0),
        "domains": list(ctx.get("structure", {}).keys())
    }
    with open(MEM_PATH, "w") as f:
        json.dump(mem, f, indent=2)

def run():
    print("[CTX] building...")
    ctx = build_context()
    save_context(ctx)
    save_memory(ctx)
    print(f"[CTX] done: {ctx['total_files']} files")

if __name__ == "__main__":
    run()
