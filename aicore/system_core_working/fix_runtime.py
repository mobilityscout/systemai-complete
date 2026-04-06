import os, json

# -------- FIX INTELLIGENCE --------
file_path = "/root/aicore/intelligence_runtime.py"

if os.path.exists(file_path):
    with open(file_path, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:

        # FIX: ensure domain/role always defined
        if "for path in files:" in line:
            new_lines.append(line)
            new_lines.append("        domain = 'unknown'\n")
            new_lines.append("        role = 'unknown'\n")
            continue

        new_lines.append(line)

    with open(file_path, "w") as f:
        f.writelines(new_lines)

    print("[FIX] intelligence_runtime patched")


# -------- FIX MANAGER --------
mgr_path = "/root/aicore/ai_manager.py"

if os.path.exists(mgr_path):
    with open(mgr_path, "r") as f:
        content = f.read()

    if "def is_valid" not in content:
        content = (
            "def is_valid(data):\n"
            "    return data.get('decision') not in ['ignore']\n\n"
        ) + content

    with open(mgr_path, "w") as f:
        f.write(content)

    print("[FIX] ai_manager patched")


print("[FIX] done")
