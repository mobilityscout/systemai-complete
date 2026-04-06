import json, subprocess

data = json.loads(
    subprocess.check_output("python3 /root/aicore/semantic.py", shell=True)
)

good = []
bad = []

for base in data:
    for f in data[base]:
        if f["score"] >= 0.7:
            good.append(f)
        else:
            bad.append(f)

print("GOOD:", len(good))
print("BAD:", len(bad))

print("\nTOP GOOD FILES:")
for g in good[:10]:
    print(g)
