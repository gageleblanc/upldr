from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr_libs.config_utils.loader import Loader
import json
from pathlib import Path


class main:
    def __init__(self):
        self.spec = {
            "desc": 'Search remote for files',
            "name": 'search',
            "positionals": [
                {
                    "name": "file",
                    "metavar": "FILE",
                    "help": "File name to search for",
                    "default": False,
                    "type": str
                }
            ],
            "flags": [
                {
                    "names": ['-d', '--debug'],
                    "help": "Add extended output.",
                    "required": False,
                    "default": False,
                    "action": "store_true",
                    "type": bool
                },
                {
                    "names": ['-a', '--address'],
                    "help": "IP address of the Hue bridge",
                    "required": False,
                    "type": str,
                    "default": "192.168.1.1"
                }
            ]
        }
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.logger = Util.configure_logging(args, __name__)
        self.home = str(Path.home())
        self.config_dir = "%s/.config/upldr" % self.home
        self.config_path = "%s/.config/upldr/indexes.json" % self.home
        self.paths = []
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        try:
            config_loader = Loader(self.config_path, auto_create=True, keys=['indexes'])
            self.config = config_loader.get_config()
        except TypeError as type_error:
            self.logger.fatal(type_error)
            exit(1)
        self.logger.debug("File: " + self.args.file)
        self.getpath(self.config.indexes, self.args.file)
        self.logger.debug(self.paths)
        self.display_results()

    def display_results(self):
        for path_parts in self.paths:
            print("%s\r\nRemote: %s\r\n  Category: %s\r\n       Tag: %s\r\n%s\r\n" % ("="*30, path_parts[0], path_parts[1], path_parts[2], "="*30))

    def getpath(self, nested_dict, value, prepath=()):
        for k, v in nested_dict.items():
            path = prepath + (k,)
            self.logger.debug("Looking in: " + k)
            self.logger.debug("Dict: " + json.dumps(v))
            if v == value:
                return path
            elif isinstance(v, dict):
                self.logger.debug("Recurse")
                self.getpath(v, value, path)
            elif isinstance(v, list):
                self.logger.debug("%s is list" % k)
                self.logger.debug(v)
                if value in v:
                    self.logger.debug("Found!")
                    self.paths.append(path)
