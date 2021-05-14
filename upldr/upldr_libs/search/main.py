from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools


class main:
    def __init__(self):
        self.spec = {
            "desc": 'Search remote for files',
            "name": 'search',
            "positionals": [],
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
