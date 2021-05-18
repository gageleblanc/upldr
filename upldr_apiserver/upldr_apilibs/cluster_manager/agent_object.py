import queue
import socket


class AgentObject:
    def __init__(self, client: socket.socket, name: str, addr: str):
        self.socket: socket.socket = client
        self.name: str = name
        self.port = client.getsockname()
        self.addr: str = addr
        self.listen = True
        self.command_queue = queue.Queue()
