from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr_apilibs.apiserver import ApiServer
from pathlib import Path

class main:
    def __init__(self):
        self.spec = {
            "desc": "Serve apiserver",
            "name": "api",
            "positionals": [],
            "flags": [
                {
                    "names": ["--destination"],
                    "help": "Local upload destination",
                    "required": False,
                    "default": False,
                    "type": str
                },
                {
                    "names": ["--port"],
                    "help": "Local port to bind slave to.",
                    "default": False,
                    "required": True,
                    "type": int
                },
                {
                    "names": ["--bind-addr"],
                    "help": "Bind address for upload slave.",
                    "required": False,
                    "default": "localhost",
                    "type": str
                },
                {
                    "names": ["--timeout"],
                    "help": "Time in seconds before slave times out waiting for connection.",
                    "required": False,
                    "default": 30,
                    "type": int
                },
                {
                    "names": ["--resume"],
                    "help": "Resume upload",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                }
            ]
        }
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.upldr_config_dir = self.user_home + "/.config/upldr"
        config_dir = Path(self.upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        ApiServer(bind_addr=self.args.bind_addr, port=self.args.port)

