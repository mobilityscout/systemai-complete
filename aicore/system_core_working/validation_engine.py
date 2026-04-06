import py_compile

def validate(path):

    try:
        py_compile.compile(path, doraise=True)
        return True, "ok"
    except Exception as e:
        return False, str(e)
