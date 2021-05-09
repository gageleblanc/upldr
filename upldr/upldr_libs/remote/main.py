from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr_libs.config_utils.loader import Loader
from pathlib import Path

class main:
    def __init__(self):
        self.spec = {
            "desc": "Manages remote apiserver configurations.",
            "name": "remote",
            "positionals": [],
            "subcommands": [
                {
                    "name": "add",
                    "desc": "Add remote to config",
                    "positionals": [
                        {
                            "name": "name",
                            "metavar": "NAME",
                            "help": "Remote Name",
                            "default": False,
                            "type": str
                        },
                        {
                            "name": "url",
                            "metavar": "URL",
                            "help": "Remote URL",
                            "default": False,
                            "type": str
                        }
                    ],
                    "flags": [
                        {
                            "names": ["--port"],
                            "help": "Used to specify remote port other than the default (25565)",
                            "default": 25565,
                            "required": False,
                            "type": int
                        },
                        {
                            "names": ["--scheme"],
                            "help": "Used to specify remote scheme other than the http.",
                            "default": "http",
                            "required": False,
                            "type": str
                        }
                    ]
                },
                {
                    "name": "remove",
                    "desc": "Remove remote from config",
                    "positionals": [
                        {
                            "name": "name",
                            "metavar": "NAME",
                            "help": "Remote Name",
                            "default": False,
                            "type": str
                        }
                    ],
                    "flags": []
                },
                {
                    "name": "set-default",
                    "desc": "Set default remote to use",
                    "positionals": [
                        {
                            "name": "name",
                            "metavar": "NAME",
                            "help": "Remote Name",
                            "default": False,
                            "type": str
                        }
                    ],
                    "flags": []
                },
                {
                    "name": "list",
                    "desc": "List remotes",
                    "positionals": [],
                    "flags": []
                }
            ],
            "flags": [
                {
                    "names": ["--debug"],
                    "help": "Local upload destination",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                }
            ]
        }
        self.command_methods = {
            "add": self.add_remote,
            "remove": self.remove_remote,
            "set-default": self.set_default,
            "list": self.list_remotes
        }
        args = arg_tools.build_nested_subparsers(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
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
        self.command_methods[self.args.subcmd]()

    def add_remote(self):
        remote_name = self.args.name
        remote_url = self.args.url
        remote_port = self.args.port
        remote_scheme = self.args.scheme
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

    def remove_remote(self):
        remote_name = self.args.name
        if not isinstance(self.config_object.remotes, dict):
            return
        if remote_name not in self.config_object.remotes:
            return
        del self.config_object.remotes[remote_name]
        self.config_object.write_config()

    def set_default(self):
        remote_name = self.args.name
        self.config_object.default = remote_name
        self.config_object.write_config()

    def list_remotes(self):
        for name,remote in self.config_object.remotes.items():
            print("%s\t%s:%d" % (name, remote['url'], remote['port']))
