class ModuleAnalyzer:

    def analyze(self, path):

        result = {
            "syntax": "ok",
            "runtime": "ok",
            "contract": "ok",
            "error": None
        }

        try:
            code = open(path).read()

            compile(code, path, "exec")

            namespace = {}
            exec(code, namespace)

            if "run" not in namespace:
                result["contract"] = "fail"
                return result

            namespace["run"]()

        except Exception as e:
            result["syntax"] = "fail"
            result["runtime"] = "fail"
            result["error"] = str(e)

        return result
