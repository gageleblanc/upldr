from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr_libs.config_utils.loader import Loader
from pathlib import Path
import yaml
import json
import requests
import socket
import time
import os
from sys import platform


class main:
    def __init__(self):
        self.spec = {
            "desc": "Handles uploads to non-cloud based remotes.",
            "name": "put",
            "positionals": [
                {
                    "name": "name",
                    "metavar": "NAME",
                    "help": "Source file to upload",
                    "default": False,
                    "type": str
                }
            ],
            "flags": [
                {
                    "names": ["--remote"],
                    "help": "Name of remote to use",
                    "required": False,
                    "default": False,
                    "type": str
                },
                {
                    "names": ["-c", "--category"],
                    "help": "Category for upload.",
                    "required": False,
                    "default": "default",
                    "type": str
                },
                {
                    "names": ["-t", "--tag"],
                    "help": "Tag for upload.",
                    "required": False,
                    "default": "default",
                    "type": str
                },
                {
                    "names": ["--timeout"],
                    "help": "Amount of time in seconds to wait before connecting to upload slave. Often there is a delay.",
                    "default": 1,
                    "required": False,
                    "type": int
                },
                {
                    "names": ["--resume"],
                    "help": "Resume upload",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                },
                {
                    "names": ["--debug"],
                    "help": "Debug output",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                }
            ]
        }
        # parser = arg_tools.build_full_parser(self.spec)
        # subparser = parser.add_subparsers(dest='cmd', description='Uploads file to remote')
        # parser_baz = subparser.add_parser('put', help='Uploads file to remote.', description='Uploads file to remote.')
        # parser_baz.add_argument('name', help="Name of the file to be uploaded.")
        # parser_baz.add_argument('-r', '--remote', help="Name of the remote to use.", required=False, default=False)
        # parser_baz.add_argument('-m', '--manual', help="Don't hit api for socket", action='store_true', required=False, default=False)
        # parser_baz.add_argument('--debug', help="Enable debug", action='store_true', required=False, default=False)
        # parser_baz.add_argument('-p', '--port', help="Port for manual mode", required=False, default=False)
        # parser_baz.add_argument('-a', '--remote-host', help="Remote host to use instead of configured remote", required=False, default=False)
        # parser_baz.add_argument('-c', '--category', help="Category for uploaded file", required=False, default='default')
        # parser_baz.add_argument('-t', '--tag', help="Tag for uploaded file", required=False, default='default')
        # parser_baz.add_argument('--resume-pos', help="File position to resume download from", required=False, type=int, default=False)
        # parser_baz.add_argument('--resume', help="Send request to resume this upload", action='store_true', required=False,
        #                         default=False)
        #
        # args = parser.parse_args()
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.remote_config_dir = self.user_home + "/.config/upldr"
        self.remote_config = self.remote_config_dir + "/config.json"
        config_dir = Path(self.remote_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        try:
            config_loader = Loader(self.remote_config, auto_create=True, keys=['default', 'remotes'])
            self.config = config_loader.get_config()
        except TypeError as type_error:
            self.log.fatal(type_error)
            exit(1)
        self.make_request()
        # self.manual_mode()
        # if self.args.manual:
        #     self.manual_mode()
        # else:
        #     self.make_request(self.args.resume)

    def make_request(self, resume=False):
        if self.args.remote:
            try:
                remote = self.config.remotes[self.args.remote]
            except KeyError:
                self.log.fatal("Remote \"%s\" not found in config." % self.args.remote)
                exit(1)
        else:
            remote = self.config.remotes[self.config.default]
        remote['timeout'] = self.args.timeout
        # remote["url"] = self.args.remote_host
        # remote["port"] = self.args.port
        # remote["timeout"] = self.args.timeout

        # remote = self.get_repo()
        # remote_scheme = remote['scheme']
        # remote_url = remote['url']
        # remote_port = remote['port']
        remote_base_url = "%s://%s:%d" % (remote['scheme'], remote['url'], remote['port'])
        file_path = self.args.name
        if platform == "win32":
            file_name = self.args.name.split('\\')[-1]
        else:
            file_name = self.args.name.split('/')[-1]
        if resume:
            request = {'filename': file_name, 'type': 'upldr', 'name': file_name, 'category': self.args.category,
                       'tag': self.args.tag, 'resume': True}
        else:
            request = {'filename': file_name, 'type': 'upldr', 'name': file_name, 'category': self.args.category,
                       'tag': self.args.tag}
        # params = json.dumps(request).encode('utf8')
        req = requests.post(remote_base_url, json=request)
        response = req.json()
        self.log.debug("Response: " + json.dumps(response))
        remote['sock_port'] = response['port']
        time.sleep(int(remote['timeout']))
        if resume:
            self.send_file(remote, file_path, response["stats"]["size"])
        else:
            self.send_file(remote, file_path)

    def retry(self):
        self.log.warn("Upload failed... Trying to resume.")
        self.make_request(True)

    def manual_mode(self):
        remote = {'sock_port': self.args.port}
        if self.args.remote_host:
            remote['url'] = self.args.remote_host
        file_path = self.args.name
        # file_name = self.args.name.split('/')[-1]
        if "resume_pos" in self.args and self.args.resume_pos:
            self.send_file(remote, file_path, self.args.resume_pos)
        else:
            self.send_file(remote, file_path)

    def send_file(self, remote, file, pos=False):
        before = time.time()
        self.log.info("Beginning file transfer...")
        self.log.debug("Connecting to socket at " + remote['url'] + " on " + str(remote['sock_port']))
        s = socket.socket()
        s.connect((remote['url'], int(remote['sock_port'])))
        file_size = os.path.getsize(file)
        f = open(file, "rb")
        if pos:
            if pos < 0:
                pos = 0
            self.log.debug("Restarting upload at %d" % pos)
            f.seek(pos)
        # buf_size = int(file_size / 4)
        buf_size = 8192
        self.log.debug("Calculated buffer size: " + str(buf_size))
        buf = f.read(buf_size)
        total_len = f.tell()
        try:
            while buf:
                total_len += len(buf)
                print("\r                                     \rSent %s/%s" % (self.sizeof_fmt(total_len), self.sizeof_fmt(file_size)), end="", flush=True)
                s.send(buf)
                buf = f.read(buf_size)
            s.close()
        except BrokenPipeError as _:
            print("\n", end="", flush=True)
            self.retry()
            return

        print("\n", end="", flush=True)
        after = time.time()
        self.log.info("File transfer finished in %d seconds!" % (after - before))

    def get_repo(self):
        config = self.open_config()
        if not self.args.remote:
            remote_name = config['default']
            return config[remote_name]
        else:
            return config[self.args.remote]

    def open_config(self):
        try:
            with open(self.remote_config, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    print("Invalid yaml in cloud config!")
                    exit(1)
        except FileNotFoundError as f:
            self.log.warn("No config found at " + self.remote_config + ", initializing empty dict for config...")
            config = {}
        return config

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)
