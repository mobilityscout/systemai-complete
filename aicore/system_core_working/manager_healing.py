import os

def analyze_error(error_msg):

    if "invalid character" in error_msg:
        return "invalid_char"

    if "SyntaxError" in error_msg:
        return "syntax"

    return "unknown"


def fix_file(path, error_type):

    try:
        with open(path, "r") as f:
            lines = f.readlines()

        fixed = []

        for line in lines:

            if error_type == "invalid_char":
                line = line.encode("ascii", "ignore").decode()

            if line.strip().startswith("//"):
                line = "#" + line.strip()[2:] + "\n"

            fixed.append(line)

        with open(path, "w") as f:
            f.writelines(fixed)

        return True

    except:
        return False
