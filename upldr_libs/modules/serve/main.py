import sys
import subprocess
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from pathlib import Path
import socket

class main:
    def __init__(self):
        parser = arg_tools.build_full_parser()
        subparser = parser.add_subparsers(dest='cmd', description='Starts an api server or standalone slave.')
        parser_baz = subparser.add_parser('serve', help='Starts an api server or standalone slave.', description='Starts an api server or standalone slave.')
        parser_baz.add_argument('mode', help="Server mode. This can be api or standalone")
        parser_baz.add_argument('--destination', help="Upload destination", required='standalone' in sys.argv)
        parser_baz.add_argument('--port', help="Port for slave to bind to", required=True)

        if "standalone" in sys.argv:
            parser_baz.add_argument('--native', help="Use native python instead of java lib", required=False, default=False, action='store_true')

        if "--native" in sys.argv:
            parser_baz.add_argument('--bind-addr', help="Address for slave to bind to", required=False, default='localhost')
            parser_baz.add_argument('--timeout', help="Time in seconds before server times out", type=int, required=False,
                                    default=30)

        args = parser.parse_args()
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
        if self.args.mode == 'standalone':
            if self.args.native:
                self.run_standalone_native()
            else:
                self.run_standalone_slave()
        elif self.args.mode == 'api':
            self.run_api_server()
        else:
            parser.print_help()

    def run_standalone_native(self):
        self.log.info("Starting native standalone upload slave on port " + self.args.port + " and saving file to " + self.args.destination)
        s = socket.socket()
        host = self.args.bind_addr
        port = self.args.port
        self.log.info("Binding to " + host + ":" + port)
        s.bind((host, int(port)))
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
        while (l):
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