from clilib.util.util import Util
import socket
import time
import os
import requests
import json
from upldr_libs.config_utils.loader import Loader
from sys import platform
from pathlib import Path
import sys


class PutApi:
    def __init__(self, args):
        self.args = args
        self.log = Util.configure_logging(args, name=__name__)

    @staticmethod
    def get_remotes():
        log = Util.configure_logging(name=__name__)
        user_home = str(Path.home())
        remote_config_dir = user_home + "/.config/upldr"
        remote_config = remote_config_dir + "/config.json"
        config_dir = Path(remote_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        try:
            config_loader = Loader(remote_config, auto_create=True, keys=['default', 'remotes'])
            return config_loader.get_config()
        except TypeError as type_error:
            log.fatal(type_error)
            sys.exit(1)

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
            self.log.fatal("Upload failed: Broken pipe.")
            # print("\n", end="", flush=True)
            # self.retry()
            return

        print("\n", end="", flush=True)
        after = time.time()
        self.log.info("File transfer finished in %d seconds!" % (after - before))

    def make_request(self, config=None, rem=None, timeout=None, name=None, category=None, tag=None, resume=False):
        if not config.remotes:
            self.log.fatal("Must specify remotes config")
            sys.exit(1)
        if rem:
            try:
                remote = config.remotes[rem]
            except KeyError:
                self.log.fatal("Remote \"%s\" not found in config." % rem)
                sys.exit(1)
        else:
            remote = config.remotes[config.default]
        remote['timeout'] = timeout
        # remote["url"] = self.args.remote_host
        # remote["port"] = self.args.port
        # remote["timeout"] = self.args.timeout

        # remote = self.get_repo()
        # remote_scheme = remote['scheme']
        # remote_url = remote['url']
        # remote_port = remote['port']
        remote_base_url = "%s://%s:%d" % (remote['scheme'], remote['url'], remote['port'])
        file_path = name
        if platform == "win32":
            file_name = name.split('\\')[-1]
        else:
            file_name = name.split('/')[-1]
        if resume:
            request = {'filename': file_name, 'type': 'upldr', 'name': file_name, 'category': category,
                       'tag': tag, 'resume': True}
        else:
            request = {'filename': file_name, 'type': 'upldr', 'name': file_name, 'category': category,
                       'tag': tag}
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

    def sizeof_fmt(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)