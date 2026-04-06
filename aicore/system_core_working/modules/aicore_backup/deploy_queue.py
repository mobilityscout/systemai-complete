from aicore.state_manager import StateManager


class DeployQueue:

    def __init__(self, tenant_id):
        self.state = StateManager(tenant_id)

    def add(self, work_package):

        queue = self.state.get_queue()
        queue.append(work_package)
        self.state.set_queue(queue)

        return {"status": "queued"}

    def get_next(self):

        queue = self.state.get_queue()

        if not queue:
            return None

        wp = queue.pop(0)
        self.state.set_queue(queue)

        return wp
