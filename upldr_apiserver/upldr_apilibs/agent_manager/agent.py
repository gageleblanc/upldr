import socket
import json
import time
from clilib.util.util import Util
from upldr_libs.serve import slave
import threading


class Agent:
    def __init__(self, cluster_host, cluster_port):
        self.log = Util.configure_logging(name=__name__)
        self.cluster_host = cluster_host
        self.cluster_port = cluster_port
        self.listen = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.cluster_host, int(self.cluster_port)))
        reg_object = {
            "token": "1qaz@WSX",
            "name": "test-agent"
        }
        reg_str = json.dumps(reg_object) + "\n"
        # reg_str.join(bytes('\0', 'utf-8'))
        self.sock.send(reg_str.encode('utf-8'))
        self._agent_listener()
        # time.sleep(5)
        # hb = json.dumps({
        #     "heartbeat": time.time()
        # }) + "\n"
        # self.sock.send(hb.encode('utf-8'))

    def _agent_listener(self):
        self.log.info("Listening for commands from [%s]" % self.cluster_host)
        while self.listen:
            msg = b''
            read = True
            while read:
                msg += self.sock.recv(1024)
                if msg.endswith(b'\n'):
                    self.log.debug("Break read for " + msg.decode()[:-1])
                    read = False
            request = json.loads(msg.decode())
            if request["Command"]["type"] == "upload":
                self._start_slave(request["Command"])

    def _start_slave(self, response):

        def free_port():
            free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            free_socket.bind(('0.0.0.0', 0))
            free_socket.listen(5)
            port = free_socket.getsockname()[1]
            free_socket.close()
            return port

        rand_port = free_port()
        res = json.dumps({
            "port": rand_port
        }) + "\n"
        self.sock.send(res.encode('utf-8'))
        category = response["category"]
        tag = response["tag"]
        if "\\" in response["filename"]:
            filename = response["filename"].split("\\")[-1]
        else:
            filename = response["filename"].split("/")[-1]
        port = rand_port

        config, destination = slave.slave_environment(category, tag, filename)
        threading.Thread(target=slave.run_standalone_native, args=(config.host, port, int(config.timeout), destination)).start()
