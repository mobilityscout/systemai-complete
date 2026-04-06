import os, json

BASE = "/root/aicore/recovered_modules"

def run():

    modules = []

    for root, dirs, files in os.walk(BASE):

        py_files = [f for f in files if f.endswith(".py")]

        if len(py_files) > 5:

            modules.append({
                "path": root,
                "files": len(py_files),
                "type": "python_module"
            })

    return modules

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
