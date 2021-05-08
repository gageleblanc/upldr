from clilib.util.util import Util
from pathlib import Path
import socket
import threading


class Slave:
    def __init__(self, host, port, destination, timeout):
        self.host = host
        self.port = port
        self.dest = destination
        self.timeout = timeout
        self.log = Util.configure_logging(name=__name__)
        th = threading.Thread(target=self.run_standalone_native)
        th.start()

    def run_standalone_native(self):
        self.log.info("Starting native standalone upload slave on port %d and saving file to %s" % (self.port, self.dest))
        s = socket.socket()
        self.log.info("Binding to %s:%d" % (self.host, self.port))
        s.bind((self.host, int(self.port)))
        # if self.args.resume:
        #     f = open(self.args.destination, 'ab')
        #     if f.tell() > 1500:
        #         f.seek(-1500, 1)
        #     else:
        #         f.seek(0)
        #     self.log.info("Resuming upload from %d" % f.tell())
        # else:
        #     f = open(self.args.destination, 'wb')
        f = open(self.dest, 'wb')
        self.log.info("Listening with %d second timeout..." % self.timeout)
        s.settimeout(int(self.timeout))
        s.listen(5)
        try:
            c, addr = s.accept()
        except socket.timeout as ex:
            self.log.fatal("No clients connected before timeout. Exiting.")
            exit(1)
        self.log.info("Accepted connection")
        l = c.recv(8192)
        while l:
            f.write(l)
            l = c.recv(8192)
        f.close()
        self.log.info("Transfer complete")
        c.close()