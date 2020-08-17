import sys
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from pathlib import Path
import yaml

class main:
    def __init__(self):
        parser = arg_tools.build_full_parser()
        subparser = parser.add_subparsers(dest='cmd',
                                          description='Sets up a remote for uploads. This can be specified in the upload command.')
        parser_baz = subparser.add_parser('setup',
                                          help='Sets up a remote for uploads. This can be specified in the upload command.',
                                          description='Sets up a remote for uploads. This can be specified in the upload command.')
        parser_baz.add_argument('-l', help="List remotes", action='store_true', required=False, default=False)
        parser_baz.add_argument('-n', '--name', help="Name of the remote to be added.", required='-l' not in sys.argv)
        parser_baz.add_argument('-u', '--remote-url', help="API Url for the remote.", required=False)
        parser_baz.add_argument('-s', '--scheme', help="API scheme for the remote.", required=False)
        parser_baz.add_argument('-p', '--port', help="API port for the remote.", required=False)
        parser_baz.add_argument('-t', help="Socket timeout", required=False, default=5)
        parser_baz.add_argument('--debug', help="Enable debug mode", action='store_true', required=False, default=False)
        parser_baz.add_argument('-a', '--add', help="Add to config. This is the default action.", action='store_true', required=False, default=True)
        parser_baz.add_argument('-r', '--delete', help="Delete from config.", action='store_true', required=False, default=False)
        parser_baz.add_argument('-d', help="Set remote as default", action='store_true', required=False, default=False)

        args = parser.parse_args()
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.remote_config_dir = self.user_home + "/.config/upldr"
        self.remote_config = self.remote_config_dir + "/remote.yaml"
        config_dir = Path(self.remote_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        if self.args.l:
            self.dump_config()
        elif self.args.delete:
            self.delete_remote()
        elif self.args.d:
            self.set_as_default()
        else:
            self.store_remote()

    def open_config(self):
        try:
            with open(self.remote_config, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    print("Invalid yaml in cloud config!")
                    exit(1)
        except FileNotFoundError as f:
            self.log.warn("No config found at " + self.remote_config + ", initializing empty dict for config...")
            config = {}
        return config

    def dump_config(self):
        print("---\n%s" % yaml.dump(self.open_config(), default_flow_style=False))

    def write_config(self, config):
        self.log.debug("Writing config to " + self.remote_config)
        with open(self.remote_config, 'w') as file:
            yaml.dump(config, file)

    def store_remote(self):
        self.log.info("Writing remote info to config...")
        config = self.open_config()
        if len(config.keys()) < 1:
            config['default'] = self.args.name
        config[self.args.name] = {
            'name': self.args.name,
            'scheme': self.args.scheme,
            'url': self.args.remote_url,
            'port': self.args.port,
            'timeout': self.args.t
        }
        self.write_config(config)

    def delete_remote(self):
        self.log.info("Deleting remote from config...")
        config = self.open_config()
        config.pop(self.args.name)
        self.write_config(config)

    def set_as_default(self):
        self.log.info("Setting " + self.args.name + " as default remote")
        config = self.open_config()
        config['default'] = self.args.name
        self.write_config(config)
