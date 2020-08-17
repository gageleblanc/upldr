import argparse
import logging
import sys
import subprocess
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from pathlib import Path
import yaml
import json
import requests
import socket
import time
import os

class main:
    def __init__(self):
        parser = arg_tools.build_full_parser()
        subparser = parser.add_subparsers(dest='cmd', description='Uploads file to remote')
        parser_baz = subparser.add_parser('put', help='Uploads file to remote.', description='Uploads file to remote.')
        parser_baz.add_argument('name', help="Name of the file to be uploaded.")
        parser_baz.add_argument('-r', '--remote', help="Name of the remote to use.", required=False, default=False)
        parser_baz.add_argument('-m', '--manual', help="Don't hit api for socket", action='store_true', required=False, default=False)
        parser_baz.add_argument('--debug', help="Enable debug", action='store_true', required=False, default=False)
        parser_baz.add_argument('-p', '--port', help="Port for manual mode", required=False, default=False)
        parser_baz.add_argument('-a', '--remote-host', help="Remote host to use instead of configured remote", required=False, default=False)

        args = parser.parse_args()
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.remote_config_dir = self.user_home + "/.config/upldr"
        self.remote_config = self.remote_config_dir + "/remote.yaml"
        config_dir = Path(self.remote_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        if self.args.manual:
            self.manual_mode()
        else:
            self.make_request()

    def make_request(self):
        remote = self.get_repo()
        remote_scheme = remote['scheme']
        remote_url = remote['url']
        remote_port = remote['port']
        remote_base_url = remote_scheme + remote_url + ":" + remote_port
        remote_api_path = '/api/job/upload'
        remote_url = remote_base_url + remote_api_path
        file_path = self.args.name
        file_name = self.args.name.split('/')[-1]
        request = {'filename': file_name, 'type': 'upldr', 'name': file_name}
        # params = json.dumps(request).encode('utf8')
        req = requests.post(remote_url, json=request)
        response = req.json()
        # print(response.read().decode('utf-8'))
        self.log.debug("Response: " + json.dumps(response))
        remote['sock_port'] = response['port']
        time.sleep(int(remote['timeout']))
        self.send_file(remote, file_path)

    def manual_mode(self):
        remote = self.get_repo()
        remote['sock_port'] = self.args.port
        if self.args.remote_host:
            remote['url'] = self.args.remote_host
        file_path = self.args.name
        # file_name = self.args.name.split('/')[-1]
        self.send_file(remote, file_path)

    def send_file(self, remote, file):
        before = time.time()
        self.log.info("Beginning file transfer...")
        self.log.debug("Connecting to socket at " + remote['url'] + " on " + str(remote['sock_port']))
        s = socket.socket()
        s.connect((remote['url'], int(remote['sock_port'])))
        file_size = os.path.getsize(file)
        f = open(file, "rb")
        # buf_size = int(file_size / 4)
        buf_size = 8192
        self.log.debug("Calculated buffer size: " + str(buf_size))
        buf = f.read(buf_size)
        total_len = 0
        while buf:
            total_len += len(buf)
            print("\r                                     \rSent %s/%s" % (self.sizeof_fmt(total_len), self.sizeof_fmt(file_size)), end="", flush=True)
            s.send(buf)
            buf = f.read(buf_size)
        s.close()

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
