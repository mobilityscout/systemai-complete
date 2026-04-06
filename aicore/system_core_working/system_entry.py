from aicore.ai_manager import AIManager


class SystemEntry:

    def __init__(self, tenant_id="t1"):
        self.ai = AIManager(tenant_id)

    def handle(self, raw):
        return self.ai.handle(raw)
