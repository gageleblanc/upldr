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
                self._start_slave(request["Command"], request["JobID"])

    def _start_slave(self, response, job_id):

        def free_port():
            free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            free_socket.bind(('0.0.0.0', 0))
            free_socket.listen(5)
            port = free_socket.getsockname()[1]
            free_socket.close()
            return port

        rand_port = free_port()
        res_dict = {
            "Type": "port",
            "JobID": job_id,
            "Data": {
                "port": rand_port
            }
        }
        res = json.dumps(res_dict) + "\n"
        self.sock.send(res.encode('utf-8'))
        category = response["category"]
        tag = response["tag"]
        if "\\" in response["filename"]:
            filename = response["filename"].split("\\")[-1]
        else:
            filename = response["filename"].split("/")[-1]
        port = rand_port

        config, destination = slave.slave_environment(category, tag, filename)
        threading.Thread(target=self._run_agent_slave, args=(config.host, port, int(config.timeout), destination, job_id)).start()

    def _run_agent_slave(self, host, port, timeout, dest, job_id):
        log = Util.configure_logging(name=__name__)
        log.info("Begin native upload slave")
        log.info("Starting native standalone upload slave on port %d and saving file to %s" % (port, dest))
        s = socket.socket()
        log.info("Binding to %s:%d" % (host, port))
        s.bind((host, int(port)))
        # if self.args.resume:
        #     f = open(self.args.destination, 'ab')
        #     if f.tell() > 1500:
        #         f.seek(-1500, 1)
        #     else:
        #         f.seek(0)
        #     self.log.info("Resuming upload from %d" % f.tell())
        # else:
        #     f = open(self.args.destination, 'wb')
        f = open(dest, 'wb')
        log.info("Listening with %d second timeout..." % timeout)
        s.settimeout(int(timeout))
        s.listen(5)
        try:
            c, addr = s.accept()
        except socket.timeout:
            log.warn("No clients connected before timeout. Exiting.")
            self._job_finished(job_id)
            return
        log.info("Accepted connection")
        l = c.recv(8192)
        while l:
            f.write(l)
            l = c.recv(8192)
        f.close()
        log.info("Transfer complete")
        c.close()
        self._job_finished(job_id)
        return

    def _job_finished(self, job_id):
        self.log.info("Sending job finished status to master for job [%s]" % job_id)
        res_dict = {
            "Type": "JobFinished",
            "JobID": job_id
        }
        res = json.dumps(res_dict) + "\n"
        self.sock.send(res.encode('utf-8'))
