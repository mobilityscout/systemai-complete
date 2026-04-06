import fileinput

path = "/root/aicore/curiosity_loop.py"

lines = []

for line in open(path):

    if "def decide_action" in line:
        lines.append(line)
        lines.append("    p = path.lower()\n")
        continue

    if "return \"ignore\"" in line:
        lines.append("    # SYSTEM AWARE DECISION\n")
        lines.append("    if \"manager\" in p or \"core\" in p:\n")
        lines.append("        return \"inspect_deep\"\n")
        lines.append("    if \"runtime\" in p or \"engine\" in p:\n")
        lines.append("        return \"analyze_structure\"\n")
        lines.append("    return \"index\"\n")
        continue

    lines.append(line)

with open(path, "w") as f:
    f.writelines(lines)

print("[FIX] decision logic upgraded")
