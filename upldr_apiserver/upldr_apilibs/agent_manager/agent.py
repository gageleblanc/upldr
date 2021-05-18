import socket
import json


class Agent:
    def __init__(self, cluster_host, cluster_port):
        self.cluster_host = cluster_host
        self.cluster_port = cluster_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.cluster_host, int(self.cluster_port)))
        reg_object = {
            "token": "1qaz@WSX",
            "name": "test-agent"
        }
        reg_str = json.dumps(reg_object) + "\n"
        # reg_str.join(bytes('\0', 'utf-8'))
        self.sock.send(reg_str.encode('utf-8'))