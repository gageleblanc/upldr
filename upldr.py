#!/usr/bin/env python3
import argparse
import importlib

from clilib.util.arg_tools import arg_tools
from clilib.util.util import Util
from clilib.util.loader import Loader

modules = Loader.getActiveModules()

args, _ = arg_tools.command_parser(modules.keys())
module = importlib.import_module("modules." + args.command[0] + ".main")
#util.dump_module(args, module)
module.main()
