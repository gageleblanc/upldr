from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader
from pathlib import Path


class RemoteConfig:
    def __init__(self, config):
        self.config_object = config
        self.log = Util.configure_logging(__name__)
        self.home = str(Path.home())
        self.config_dir = "%s/.config/upldr" % self.home
        self.config_path = "%s/.config/upldr/config.json" % self.home
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        try:
            config_loader = Loader(self.config_path, auto_create=True, keys=['default', 'remotes'])
            self.config_object = config_loader.get_config()
        except TypeError as type_error:
            self.log.fatal(type_error)
            exit(1)

    def add_remote(self, name, url, port, scheme):
        remote_name = name
        remote_url = url
        remote_port = port
        remote_scheme = scheme
        self.log.debug("Adding %s:%d as %s" % (remote_url, remote_port, remote_name))
        if not isinstance(self.config_object.remotes, dict):
            self.config_object.remotes = {}
        if len(self.config_object.remotes.keys()) < 1:
            self.config_object.default = remote_name
        self.config_object.remotes[remote_name]= {
            "url": remote_url,
            "port": remote_port,
            "scheme": remote_scheme
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