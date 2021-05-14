from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from .remote_indexes import RemoteIndexes


class main:
    def __init__(self):
        self.spec = {
            "desc": 'Update remote indexes',
            "name": 'update',
            "positionals": [],
            "flags": [
                {
                    "names": ['-d', '--debug'],
                    "help": "Add extended output.",
                    "required": False,
                    "default": False,
                    "action": "store_true",
                    "type": bool
                }
            ]
        }
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.logger = Util.configure_logging(args, __name__)
        RemoteIndexes(self.args)
