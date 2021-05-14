from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader
from upldr_libs.config_utils.config import Config
from pathlib import Path


class RemoteConfig:
    def __init__(self, config: Config):
        self.config_object = config
        self.log = Util.configure_logging(__name__)

    def add_remote(self, name, url, port, scheme, timeout):
        remote_name = name
        remote_url = url
        remote_port = port
        remote_scheme = scheme
        self.log.debug("Adding %s:%d as %s" % (remote_url, remote_port, remote_name))
        if not isinstance(self.config_object.remotes, dict):
            self.config_object.remotes = {}
        if len(self.config_object.remotes.keys()) < 1:
            self.config_object.default = remote_name
        self.config_object.remotes[remote_name] = {
            "url": remote_url,
            "port": remote_port,
            "scheme": remote_scheme,
            "timeout": timeout
        }
        self.config_object.write_config()

    def remove_remote(self, name):
        remote_name = name
        if not isinstance(self.config_object.remotes, dict):
            return
        if remote_name not in self.config_object.remotes:
            return
        del self.config_object.remotes[remote_name]
        self.config_object.write_config()

    def set_default(self, name):
        remote_name = name
        self.config_object.default = remote_name
        self.config_object.write_config()