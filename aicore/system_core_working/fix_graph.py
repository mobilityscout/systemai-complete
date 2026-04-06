import fileinput

path = "/root/aicore/system_map.py"

lines = []

for line in open(path):

    # komplette alte semantic_links entfernen
    if "def semantic_links" in line:
        lines.append("def semantic_links(graph):\n")
        lines.append("    new_graph = {}\n")
        lines.append("\n")
        lines.append("    for name, data in graph.items():\n")
        lines.append("        new_graph[name] = {\n")
        lines.append("            **data,\n")
        lines.append("            'connected_to': list(set(data.get('connected_to', [])))\n")
        lines.append("        }\n")
        lines.append("\n")
        lines.append("    names = list(graph.keys())\n")
        lines.append("\n")
        lines.append("    for i in range(len(names)):\n")
        lines.append("        for j in range(i+1, len(names)):\n")
        lines.append("            a = names[i]\n")
        lines.append("            b = names[j]\n")
        lines.append("\n")
        lines.append("            wa = set(a.lower().replace('.py','').split('_'))\n")
        lines.append("            wb = set(b.lower().replace('.py','').split('_'))\n")
        lines.append("\n")
        lines.append("            if wa & wb:\n")
        lines.append("                new_graph[a]['connected_to'].append(b)\n")
        lines.append("                new_graph[b]['connected_to'].append(a)\n")
        lines.append("\n")
        lines.append("    return new_graph\n")
        break

    lines.append(line)

with open(path, "w") as f:
    f.writelines(lines)

print("[FIX] graph recursion removed")
