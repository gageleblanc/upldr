import logging
import platform
import yaml
import psutil
import multiprocessing

class Util:
  @staticmethod
  def dump_module(args, module):
    if args.debug:
      print(dir(module))

  @staticmethod
  def import_test():
    print("Import success!")

  @staticmethod
  def configure_logging(args, name):
    logFormatter = logging.Formatter(fmt='[%(asctime)s][%(name)s][%(levelname)8s] - %(message)s')
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    if args.debug:
      log.setLevel(logging.DEBUG)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(logFormatter)
    if args.debug:
      consoleHandler.setLevel(logging.DEBUG)

    log.addHandler(consoleHandler)

    return log

  @staticmethod
  def system_info():
    arch = platform.machine()
    version = platform.version()
    kernel = platform.platform()
    mem = psutil.virtual_memory().total
    cores = multiprocessing.cpu_count()
    os = platform.system()
    cpu = platform.processor()
    return {
      'os': os,
      'kernel': kernel,
      'version': version,
      'arch': arch,
      'memory': "{}G".format(mem/(1024.**3)),
      'cores': cores,
      'cpu': cpu
    }
    