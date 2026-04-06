import os, json

PATHS = [
    "/root/system_modules",
    "/root/system_auto",
    "/root/quarantine",
    "/root/generated"
]

def read_head(path):
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(200)
    except:
        return ""

def analyze_file(path):
    name = path.lower()
    content = read_head(path)

    # 🧠 Zugehörigkeit
    if "chat" in name or "http.createServer" in content:
        belongs = "self"

    elif "api" in name or "fastapi" in content:
        belongs = "self"

    elif "fix" in name or "patch" in name:
        belongs = "other_manager"

    elif name.endswith(".log") or name.startswith("."):
        belongs = "irrelevant"

    else:
        belongs = "unknown"

    # 📊 Reifegrad
    if "todo" in content:
        maturity = 0.3
    elif "fix" in name or "patch" in name:
        maturity = 0.6
    elif "server" in content or "app" in content:
        maturity = 0.8
    else:
        maturity = 0.2

    # 🚀 Potenzial
    upgradeable = maturity < 0.8 and belongs != "irrelevant"

    # 🧠 Beschreibung
    if belongs == "self":
        desc = "System-relevante Komponente (AI Manager)"

    elif belongs == "other_manager":
        desc = "Kann für andere Systeme oder Reparaturen genutzt werden"

    elif belongs == "irrelevant":
        desc = "Nicht relevant (Logs / Systemreste)"

    else:
        desc = "Unklare Funktion – prüfen"

    return {
        "file": path,
        "belongs_to": belongs,
        "maturity": maturity,
        "upgradeable": upgradeable,
        "description": desc
    }

def scan():
    results = []

    for base in PATHS:
        if not os.path.exists(base):
            continue

        for root, dirs, files in os.walk(base):
            for f in files:
                path = os.path.join(root, f)
                results.append(analyze_file(path))

    return results

if __name__ == "__main__":
    print(json.dumps(scan()))
