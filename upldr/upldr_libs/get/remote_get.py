import requests
from pathlib import Path
from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader


def get_file(remote, category, tag, filename, output=False):
    log = Util.configure_logging(name=__name__)
    file_path = "%s://%s:%s/%s/%s/%s" % (remote["scheme"], remote["url"], remote["port"], category, tag, filename)
    file_res = requests.get(file_path)
    if file_res.status_code != 200:
        log.fatal("Get failed with response: %d" % file_res.status_code)
    else:
        with open("./" + output if output else filename, 'wb') as lf:
            lf.write(file_res.text.encode('utf-8'))