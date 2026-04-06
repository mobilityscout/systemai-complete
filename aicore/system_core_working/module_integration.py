import os, json, shutil

MODULES_DIR = "/root/aicore/recovered_modules"
TARGET = "/root/aicore/system_core/modules"

os.makedirs(TARGET, exist_ok=True)

def evaluate_module(path):

    files = [f for f in os.listdir(path) if f.endswith(".py")]

    score = len(files)

    return {
        "path": path,
        "files": len(files),
        "score": score,
        "decision": "integrate" if score > 10 else "review"
    }

def run():

    results = []

    for root, dirs, files in os.walk(MODULES_DIR):

        py_files = [f for f in files if f.endswith(".py")]

        if len(py_files) > 5:

            mod = evaluate_module(root)

            results.append(mod)

            if mod["decision"] == "integrate":

                name = root.split("/")[-1]
                dst = os.path.join(TARGET, name)

                if not os.path.exists(dst):
                    shutil.copytree(root, dst)

    return results

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
