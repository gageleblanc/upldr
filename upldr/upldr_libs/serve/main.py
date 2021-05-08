import sys
import subprocess
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from pathlib import Path
import socket

class main:
    def __init__(self):
        self.spec = {
            "desc": "Handles serving an upload slave",
            "name": "serve",
            "positionals": [],
            "flags": [
                {
                    "names": ["--destination"],
                    "help": "Local upload destination",
                    "required": True,
                    "default": False,
                    "type": str
                },
                {
                    "names": ["--port"],
                    "help": "Local port to bind slave to.",
                    "default": False,
                    "required": True,
                    "type": int
                },
                {
                    "names": ["--bind-addr"],
                    "help": "Bind address for upload slave.",
                    "required": False,
                    "default": "localhost",
                    "type": str
                },
                {
                    "names": ["--timeout"],
                    "help": "Time in seconds before slave times out waiting for connection.",
                    "required": False,
                    "default": 30,
                    "type": int
                },
                {
                    "names": ["--resume"],
                    "help": "Resume upload",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                }
            ]
        }
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.upldr_config_dir = self.user_home + "/.config/upldr"
        self.lib_dir = self.user_home + "/.upldr/lib"
        self.lib_config = self.upldr_config_dir + "/libs.yaml"
        lib_dir = Path(self.lib_dir)
        lib_dir.mkdir(parents=True, exist_ok=True)
        config_dir = Path(self.upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        self.run_standalone_native()
        # if self.args.mode == 'standalone':
        #     if self.args.native:
        #         self.run_standalone_native()
        #     else:
        #         self.run_standalone_slave()
        # elif self.args.mode == 'api':
        #     self.run_api_server()
        # else:
        #     parser.print_help()

    def run_standalone_native(self):
        self.log.info("Starting native standalone upload slave on port %d and saving file to %s" % (self.args.port, self.args.destination))
        s = socket.socket()
        host = self.args.bind_addr
        port = self.args.port
        self.log.info("Binding to %s:%d" % (host, port))
        s.bind((host, int(port)))
        if self.args.resume:
            f = open(self.args.destination, 'ab')
            if f.tell() > 1500:
                f.seek(-1500, 1)
            else:
                f.seek(0)
            self.log.info("Resuming upload from %d" % f.tell())
        else:
            f = open(self.args.destination, 'wb')
        self.log.info("Listening with " + str(self.args.timeout) + " second timeout...")
        s.settimeout(int(self.args.timeout))
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

    def run_standalone_slave(self):
        self.log.info("Starting standalone upload slave on port " + self.args.port + " and saving file to " + self.args.destination)
        slave_bin = self.lib_dir + "/media-server-api/upload-slave.jar"
        slave_cmd = [
            "java", "-jar", slave_bin, self.args.port, self.args.destination
        ]
        self.run_cmd(slave_cmd)

    def run_api_server(self):
        self.log.info("Starting api server on " + self.args.port)
        api_lib = self.lib_dir + "/media-server-api"
        api_main = api_lib + "/main.js"
        api_server_cmd = [
            "nodejs", api_main, self.args.port
        ]
        self.run_cmd(api_server_cmd)

    def clone_repo(self):
        self.log.info("Creating skeleton in " + self.args.parent_dir + "/" + self.args.name)
        clone_args = [
          "git", "clone", self.args.repository, self.args.parent_dir + "/" + self.args.name
        ]
        self.run_cmd(clone_args)

    def run_cmd(self, cmd_args):
        self.log.debug("Command: " + " ".join(cmd_args))
        try:
            subprocess.run(cmd_args, stderr=sys.stderr, stdout=sys.stdout)
        except FileNotFoundError as ex:
            self.log.fatal(cmd_args[0] + " is not installed!")