from aicore.validator import Validator
from aicore.executor import WorkPackageExecutor


class DeployPipeline:
    """
    Kontrollierte Ausführung:
    validate -> execute
    """

    def __init__(self):
        self.validator = Validator()

    def run(self, wp: dict) -> dict:
        check = self.validator.validate(wp)

        if check["status"] != "ok":
            return {
                "status": "blocked",
                "validation": check
            }

        tenant_id = wp["tenant_id"]
        executor = WorkPackageExecutor(tenant_id)

        result = executor.execute(wp)

        return {
            "status": "deployed",
            "result": result
        }
