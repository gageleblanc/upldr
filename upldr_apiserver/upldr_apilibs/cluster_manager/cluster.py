import socket
from pathlib import Path
from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader as ConfigLoader
from .agent_object import AgentObject
from .scheduling import Scheduling
from .message_object import MessageObject
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
        self.events = {}

    def start(self):
        self._cluster_socket()

    def _cluster_socket(self):
        self.log.info("Starting upldr cluster...")
        # self.log.info("Starting native standalone upload slave on port %d and saving file to %s" % (port, dest))
        s = socket.socket()
        self.log.info("Binding cluster endpoint to %s:%d" % (self.config.host, self.config.port))
        s.bind((self.config.host, int(self.config.port)))
        s.listen(5)
        while True:
            c, addr = s.accept()
            ip = addr[0]
            threading.Thread(target=self._register_client, args=(c, ip)).start()
            self.log.info("Accepted connection from [%s]" % str(addr))

    def _register_client(self, client: socket.socket, addr):
        self.log.info("Registering client")
        # payload = client.recv(1024)
        # self.log.info(payload)
        msg = b''
        read = True
        while read:
            msg += client.recv(1024)
            self.log.info("Current Message [%s] Current End [%s]" % (msg, msg[-1:]))
            # self.log.info(msg.ends)
            if msg.endswith(b'\n'):
                self.log.info("break for " + msg.decode()[:-1])
                read = False
                # break
        request = json.loads(msg.decode())
        if not self._validate_registration_request(request):
            self._send_error_response(client, 500, "Malformed Request", addr)
            self.log.warn("Agent [%s] sent malformed registration request: [%s]" % (addr, json.dumps(request)))
        else:
            if request["token"] == self.config.token:
                agent = AgentObject(client, request["name"], addr)
                self.agents[addr] = agent
                self.scheduler.add_agent(agent)
                threading.Thread(target=self._agent_listener, args=(agent,)).start()
                self.log.info("Registered agent [%s]" % addr)
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

    def _fire_events(self, job_id, ty, data):
        events = self.events
        for handler in events[job_id][ty]:
            handler(data)
            self.events[job_id][ty].remove(handler)

    def _agent_listener(self, agent: AgentObject):
        self.log.info("Listening for input from [%s]" % agent.addr)
        while agent.listen:
            message = self._get_response(agent)
            self.log.info("Agent [%s] says [%s]" % (agent.name, json.dumps(message)))
            if message["JobID"] in self.events:
                if message["Type"] in self.events[message["JobID"]]:
                    self._fire_events(message["JobID"], message["Type"], message["Data"])
                elif message["Type"] == "JobFinished":
                    self.log.info("Agent [%s] reports job [%s] as finished." % (agent.name, message["JobID"]))
                    self._job_finished(agent.addr, message["JobID"])
                else:
                    self.log.info("No handlers for event type [%s] with job ID [%s]" % (message["Type"], message["JobID"]))
            elif message["Type"] == "JobFinished":
                self.log.info("Agent [%s] reports job [%s] as finished." % (agent.name, message["JobID"]))
                self._job_finished(agent.addr, message["JobID"])
                # self.scheduler.done(agent.addr, message["JobID"])
            else:
                self.log.info("No handlers found for event type [%s] from [%s]" % (message["Type"], agent.name))

    def _job_finished(self, agent: str, job_id: str):
        self.scheduler.done(agent, job_id)
        if job_id in self.events:
            del self.events[job_id]

    def _get_response(self, agent: AgentObject):
        msg = b''
        read = True
        while read:
            msg += agent.socket.recv(1024)
            if msg.endswith(b'\n'):
                self.log.info("Received message [%s] from agent [%s]" % (msg.decode('utf-8'), agent.addr))
                read = False

        response = json.loads(msg.decode('utf-8'))
        return response

    def _wait_for_port(self, agent: AgentObject):
        wait = True
        while wait:
            response = self._get_response(agent)
            if "port" in response:
                return response
            else:
                agent.command_queue.put(response)

    def on(self, job_id=None, ty=None, func=None):
        if job_id not in self.events:
            self.events[job_id] = {}
        if ty not in self.events[job_id]:
            self.events[job_id][ty] = []
        self.events[job_id][ty].append(func)

    def _send_command(self, worker: str, job_id: str, command: dict):
        agent = self._get_agent(worker)
        if agent:
            command_bytes = json.dumps({
                "Response": 1200,
                "Command": command,
                "JobID": job_id
            }) + "\n"
            command_bytes = command_bytes.encode('utf-8')
            client = agent.socket
            client.send(command_bytes)
            # return worker, job_id
        else:
            self.log.warn("Cannot send command to agent.")

    def send_command(self, command: dict):
        worker, job_id = self.scheduler.worker()
        self.log.info("Sending command with ID [%s] to [%s]" % (job_id, worker))
        threading.Thread(target=self._send_command, args=(worker, job_id, command)).start()
        return worker, job_id
