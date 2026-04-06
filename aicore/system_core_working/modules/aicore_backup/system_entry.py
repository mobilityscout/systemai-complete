from aicore.ai_manager import AIManager


class SystemEntry:
    """
    Dünner Einstiegspunkt für Chat/UI.
    Keine Logik hier – nur Delegation an den AI Manager.
    """

    def __init__(self, tenant_id: str = "t1"):
        self.ai = AIManager(tenant_id=tenant_id)

    def handle(self, raw_input: str) -> dict:
        return self.ai.handle_chat(raw_input)

    def immune_tick(self) -> list[dict]:
        return self.ai.tick_immune()
