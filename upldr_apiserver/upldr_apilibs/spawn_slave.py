from pathlib import Path
from upldr_libs.config_utils.loader import Loader as ConfigLoader
from upldr_libs.serve.slave import Slave


class SpawnSlave:
    def __init__(self, category, tag, port, filename):
        self.user_home = str(Path.home())
        self.upldr_config_dir = self.user_home + "/.config/upldr_apiserver"
        config_dir = Path(self.upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = str(config_dir) + "/slave_config.json"
        config_loader = ConfigLoader(config=config_file, keys=["data_dir", "timeout", "host"], auto_create=True)
        self.config = config_loader.get_config()
        parent_dir = "%s/%s/%s" % (self.config["data_dir"], category, tag)
        Path(parent_dir).mkdir(parents=True, exist_ok=True)
        destination = "%s/%s/%s/%s" % (self.config["data_dir"], category, tag, filename)
        Slave(host=self.config["host"], port=port, destination=destination, timeout=int(self.config["timeout"]))