import sys
import subprocess
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from pathlib import Path
import yaml
import os

class main:
    def __init__(self):
        parser = arg_tools.build_full_parser()
        subparser = parser.add_subparsers(dest='cmd',
                                          description='Tools for managing upldr external libraries')
        parser_baz = subparser.add_parser('libs', help='Tools for managing upldr external libraries',
                                          description='Tools for managing upldr external libraries')
        parser_baz.add_argument('command', help="Command to run.")
        parser_baz.add_argument('--name', help="Library name", required='delete' in sys.argv)

        args = parser.parse_args()
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.user_home = str(Path.home())
        self.upldr_config_dir = self.user_home + "/.config/upldr"
        self.lib_dir = self.user_home + "/.upldr/lib"
        self.lib_config = self.upldr_config_dir + "/libs.yaml"
        self.default_repos = {
            'media-server-api': 'https://github.com/gageleblanc/media-server-api.git'
        }
        lib_dir = Path(self.lib_dir)
        lib_dir.mkdir(parents=True, exist_ok=True)
        config_dir = Path(self.upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        # Clean this up with a map later, idiot
        if self.args.command == "install":
            self.download_default_libs()
        elif self.args.command == "delete":
            self.delete_lib()
        elif self.args.command == "list":
            self.dump_config()
        else:
            parser.print_help()

    def dump_config(self):
        print("---\n%s" % yaml.dump(self.open_config(), default_flow_style=False))

    def delete_lib(self):
        config = self.open_config()
        if self.args.name in config:
            lib = config[self.args.name]
            self.delete_lib_from_config()
            self.delete_lib_dir(lib)
        else:
            self.log.fatal("This lib doesnt exist: " + self.args.name)

    def download_default_libs(self):
        self.clone_repos()

    def clone_repos(self):
        for k,v in self.default_repos.items():
            destination = self.lib_dir + "/" + k
            self.log.info("Downloading " + k + " to " + destination)
            self.clone_repo(v, destination)
            self.log.info("Installing deps for " + k)
            self.install_deps(destination)
            lib = {
                'name': k,
                'repo': v,
                'dest': destination
            }
            self.store_lib(lib)

    def clone_repo(self, repository, destination):
        # self.log.info("Downloading to " + destination)
        clone_args = [
            "git", "clone", repository, destination
        ]
        self.run_cmd(clone_args)

    def lib_type(self, dir):
        files = os.listdir(dir)
        if "package-lock.json" in files:
            return "npm"
        else:
            return False

    def install_deps(self, destination):
        pkg_manager = self.lib_type(destination)
        if not pkg_manager:
            self.log.warn("Could not determine package manager type for " + destination)
            return
        self.log.info("Lib type: " + pkg_manager)
        if pkg_manager == "npm":
            cmd = [
                "npm", "install"
            ]
            self.run_cmd_dir(cmd, destination)

    def run_cmd(self, cmd_args):
        self.log.debug("Command: " + " ".join(cmd_args))

        try:
            subprocess.run(cmd_args, stderr=sys.stderr, stdout=sys.stdout)
        except FileNotFoundError as ex:
            self.log.fatal(cmd_args[0] + " is not installed!")

    def run_cmd_dir(self, cmd_args, cwd):
        self.log.debug("Command: " + " ".join(cmd_args))

        try:
            subprocess.run(cmd_args, stderr=sys.stderr, stdout=sys.stdout, cwd=cwd)
        except FileNotFoundError as ex:
            self.log.fatal(cmd_args[0] + " is not installed!")

    def open_config(self):
        try:
            with open(self.lib_config, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
                    print("Invalid yaml in cloud config!")
                    exit(1)
        except FileNotFoundError as f:
            self.log.warn("No config found at " + self.lib_config + ", initializing empty dict for config...")
            config = {}
        return config

    def write_config(self, config):
        with open(self.lib_config, 'w') as file:
            yaml.dump(config, file)

    def store_lib(self, lib):
        self.log.info("Writing lib info to file...")
        config = self.open_config()
        config[lib['name']] = lib
        self.write_config(config)

    def delete_lib_dir(self, lib):
        self.log.info("Removing files for " + lib['name'] + " from " + lib['dest'])
        rm_args = [
            "rm", "-rvf", lib['dest']
        ]
        self.run_cmd(rm_args)

    def delete_lib_from_config(self):
        self.log.info("Deleting " + self.args.name + " from file...")
        config = self.open_config()
        config.pop(self.args.name)
        self.write_config(config)
