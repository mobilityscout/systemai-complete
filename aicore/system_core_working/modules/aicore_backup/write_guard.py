import os
import py_compile
import tempfile


class WriteGuard:

    def safe_write(self, path, content):

        os.makedirs(os.path.dirname(path), exist_ok=True)

        # 🔴 TEMP FILE
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
            tmp_path = tmp.name
            tmp.write(content.encode())

        # 🔴 COMPILE CHECK (CRITICAL)
        try:
            py_compile.compile(tmp_path, doraise=True)
        except Exception as e:
            os.remove(tmp_path)
            return {
                "status": "rejected",
                "reason": "compile_error",
                "error": str(e)
            }

        # 🔴 ATOMIC WRITE
        os.replace(tmp_path, path)

        return {
            "status": "written",
            "path": path
        }
