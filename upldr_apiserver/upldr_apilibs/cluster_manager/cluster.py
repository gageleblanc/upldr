import socket
from pathlib import Path
from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader as ConfigLoader
from .agent_object import AgentObject
from .scheduling import Scheduling
import threading
import json


class Cluster:
    def __init__(self):
        self.log = Util.configure_logging(name=__name__)
        user_home = str(Path.home())
        upldr_config_dir = user_home + "/.config/upldr_apiserver"
        config_dir = Path(upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = str(config_dir) + "/cluster.json"
        config_loader = ConfigLoader(config=config_file, keys=["cluster_name", "dc", "host", "port", "token"], auto_create=True)
        self.scheduler = Scheduling()
        self.config = config_loader.get_config()
        self.agents = {}

    def _cluster_socket(self):
        self.log.info("Starting upldr cluster...")
        # self.log.info("Starting native standalone upload slave on port %d and saving file to %s" % (port, dest))
        s = socket.socket()
        self.log.info("Binding cluster endpoint to %s:%d" % (self.config.host, self.config.port))
        s.bind((self.config.host, int(self.config.port)))
        s.listen(5)
        while True:
            c, addr = s.accept()
            threading.Thread(target=self._register_client, args=(c, addr))
            self.log.info("Accepted connection from [%s]" % addr)

    def _register_client(self, client: socket.socket, addr):
        payload = client.recv(1024)
        msg = payload
        while payload:
            msg += payload
            payload = client.recv(1024)
        request = json.loads(msg)
        if not self._validate_registration_request(request):
            self._send_error_response(client, 500, "Malformed Request", addr)
            self.log.warn("Agent [%s] sent malformed registration request: [%s]" % (addr, json.dumps(request)))
        else:
            if request["token"] == self.config.token:
                agent = AgentObject(client, request["name"], addr)
                self.agents[addr] = agent
                self.scheduler.add_agent(agent)
            else:
                self._send_error_response(client, 401, "Invalid Registration Token.", addr)
                self.log.warn("Agent [%s] sent bad registration token: [%s]" % (addr, request["token"]))

    def _validate_registration_request(self, request):
        keys = [
            "token",
            "name"
        ]
        for key in keys:
            if key not in request:
                return False
        return True

    def _send_error_response(self, client: socket.socket, code: int, message: str, addr: str):
        client.send(json.dumps({"Response": code, "Message": message}).encode('utf-8'))
        self.log.warn("Disconnecting agent [%s] with code [%d] for: [%s]" % (addr, code, message))
        client.close()

    def _get_agent(self, addr):
        if addr in self.agents:
            return self.agents[addr]
        else:
            self.log.warn("Agent [%s] is not registered!")

    def _agent_listener(self, agent: AgentObject):
        self.log.info("Listening for input from [%s]" % agent.addr)
        while agent.listen:
            payload = agent.socket.recv(1024)
            msg = payload
            while payload:
                msg += agent.socket.recv(1024)
            request = json.loads(msg)


    def send_command(self, command: dict):
        command_bytes = json.dumps({
            "Response": 1200,
            "Command": command
        }).encode('utf-8')
        worker = self.scheduler.worker()
        agent = self._get_agent(worker)
        if agent:
            client = agent.socket
            client.send(command_bytes)
        else:
            self.log.warn("Cannot send command to agent.")
