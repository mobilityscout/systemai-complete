print('[LOG] start')
import os, sys, json

BASE = "/root/generated"

def ensure():
    os.makedirs(BASE, exist_ok=True)

def build_unknown_handler():
    path = os.path.join(BASE, "unknown_handler")
    os.makedirs(path, exist_ok=True)

    script = os.path.join(path, "handle.sh")

    with open(script, "w") as f:
        f.write("""#!/bin/bash

echo "Handling unknown files..."

SRC="/root/system_auto/unknown"
DST="/root/aicore/system_core/unknown"

mkdir -p "$DST"

if [ -d "$SRC" ]; then
  for f in "$SRC"/*; do
    if [ -f "$f" ]; then
      mv "$f" "$DST/"
      echo "MOVED: $(basename "$f")"
    fi
  done
fi

echo "DONE"
""")

    os.chmod(script, 0o755)

def run(summary):
    ensure()
    created = []

    if summary.get("unknown",0) > 0:
        build_unknown_handler()
        created.append("unknown_handler")

    return created

if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = run(data.get("summary",{}))
    print(json.dumps({"created": result}))
