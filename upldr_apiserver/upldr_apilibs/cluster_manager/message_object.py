class MessageObject:
    def __init__(self, agent: str, type: str, job: str, data: dict):
        self.agent = agent
        self.type = type
        self.job = job
        self.data = data
