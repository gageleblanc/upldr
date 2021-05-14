from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr_libs.config_utils.loader import Loader
from pathlib import Path
from .remote_get import get_file


class main:
    def __init__(self):
        self.spec = {
            "desc": 'Get file from remote',
            "name": 'get',
            "positionals": [
                {
                    "name": "category",
                    "metavar": "CATEGORY",
                    "help": "File to download",
                    "default": False,
                    "type": str
                },
                {
                    "name": "tag",
                    "metavar": "TAG",
                    "help": "File to download",
                    "default": False,
                    "type": str
                },
                {
                    "name": "name",
                    "metavar": "NAME",
                    "help": "File to download",
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
                    "names": ['-o', '--output'],
                    "help": "Output Filename",
                    "required": False,
                    "default": False,
                    "type": str
                },
                {
                    "names": ['-R', '--remote'],
                    "help": "Specify remote other than default",
                    "required": False,
                    "default": False,
                    "type": str
                }
            ]
        }
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.logger = Util.configure_logging(args, __name__)
        category = self.args.category
        tag = self.args.tag
        file = self.args.name
        self.home = str(Path.home())
        self.remotes_config_path = "%s/.config/upldr/config.json" % self.home
        try:
            config_loader = Loader(self.remotes_config_path, auto_create=True, keys=['remotes'])
            self.remotes_config = config_loader.get_config()
        except TypeError as type_error:
            self.logger.fatal(type_error)
            exit(1)

        if self.args.remote:
            try:
                remote = self.remotes_config.remotes[self.args.remote]
            except KeyError:
                self.logger.fatal("Remote [%s] does not exist." % self.args.remote)
                exit(1)
        else:
            remote = self.remotes_config.remotes[self.remotes_config.default]
        get_file(remote, category, tag, file, self.args.output)
