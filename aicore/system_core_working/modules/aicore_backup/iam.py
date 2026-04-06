class IAM:

    def approve(self, work_package):

        intent = work_package.get("intent")

        # 🔴 SIMPLE POLICY (jetzt)
        if intent == "BUILD":
            return {
                "approved": True,
                "reason": "build allowed"
            }

        return {
            "approved": False,
            "reason": "not allowed"
        }
