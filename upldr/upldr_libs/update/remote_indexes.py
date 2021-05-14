from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader
from pathlib import Path
import requests


class RemoteIndexes:
    def __init__(self, args=None):
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.home = str(Path.home())
        self.config_dir = "%s/.config/upldr" % self.home
        self.config_path = "%s/.config/upldr/indexes.json" % self.home
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        try:
            config_loader = Loader(self.config_path, auto_create=True, keys=['indexes'])
            self.config = config_loader.get_config()
        except TypeError as type_error:
            self.log.fatal(type_error)
            exit(1)
        self.remotes_config_path = "%s/.config/upldr/config.json" % self.home
        try:
            config_loader = Loader(self.remotes_config_path, auto_create=True, keys=['remotes'])
            self.remotes_config = config_loader.get_config()
        except TypeError as type_error:
            self.log.fatal(type_error)
            exit(1)
        self._update_indexes()
        self._write_indexes()

    def _write_indexes(self):
        self.config.write_config()

    def _update_index(self, name, remote):
        self.log.info("Updating remote index [%s]" % name)
        remote_url = "%s://%s:%s" % (remote['scheme'], remote['url'], remote['port'])
        try:
            index = requests.get(remote_url)
            if not isinstance(self.config.indexes, dict):
                self.config.indexes = {}
            self.config.indexes[name] = index.json()["index"]
        except requests.exceptions.ConnectionError:
            self.log.warn("Remote [%s] unreachable" % name)

    def _update_indexes(self):
        self.log.info("Updating remote indexes...")
        if not isinstance(self.remotes_config.remotes, dict):
            self.log.warn("No remotes defined")
        for name, remote in self.remotes_config.remotes.items():
            self._update_index(name, remote)
