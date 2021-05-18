from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr_apilibs.index_data import IndexData
from upldr_apilibs.http_app import HttpApp
from upldr_apilibs.cluster_manager.cluster import Cluster
from upldr_apilibs.agent_manager.agent import Agent
from pathlib import Path
import threading


class main:
    def __init__(self):
        self.spec = {
            "desc": "Handles apiserver commands. This subcommand requires upldr_apiserver",
            "name": "api",
            "positionals": [],
            "subcommands": [
                {
                    "name": "serve",
                    "desc": "Serve API Server",
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
                            "default": 25565,
                            "required": False,
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
                        },
                        {
                            "names": ["--start-cluster"],
                            "help": "Start cluster manager with api server",
                            "required": False,
                            "default": False,
                            "action": "store_true"
                        },
                    ]
                },
                {
                    "name": "agent",
                    "desc": "Start cluster agent",
                    "positionals": [],
                    "flags": [
                        {
                            "names": ["--master"],
                            "help": "Local upload destination",
                            "required": False,
                            "default": "localhost",
                            "type": str
                        },
                        {
                            "names": ["--port"],
                            "help": "Local port to bind slave to.",
                            "default": 25566,
                            "required": False,
                            "type": int
                        }
                    ]
                },
                {
                    "name": "index",
                    "desc": "Index data directory for apiserver",
                    "positionals": [],
                    "flags": []
                }
            ],
            "flags": [
                {
                    "names": ["-d", "--debug"],
                    "help": "Print extended debugging information.",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                }
            ]
        }
        args = arg_tools.build_nested_subparsers(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.upldr_config_dir = self.user_home + "/.config/upldr"
        config_dir = Path(self.upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        self.command_map = {
            "serve": self._serve,
            "index": self._index,
            "agent": self._agent
        }
        self.command_map[self.args.subcmd]()

    def _serve(self):
        api_thread = threading.Thread(target=HttpApp.start_app, args=(self.args.bind_addr, self.args.port, True if self.args.start_cluster else False))
        api_thread.start()
        # if self.args.start_cluster:
        #     cluster = Cluster()
        #     cluster_thread = threading.Thread(target=cluster.start)
        #     cluster_thread.start()

    def _agent(self):
        Agent(self.args.master, self.args.port)

    def _index(self):
        IndexData()
