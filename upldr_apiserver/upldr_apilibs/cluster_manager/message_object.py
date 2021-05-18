class MessageObject:
    def __init__(self, agent: str, type: str, args: dict):
        self.agent = agent
        self.type = type
        self.args = args