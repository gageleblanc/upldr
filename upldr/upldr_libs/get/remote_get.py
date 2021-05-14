import requests
from pathlib import Path
from clilib.util.util import Util
from upldr_libs.config_utils.loader import Loader
import sys


def get_file(remote, category, tag, filename, output=False):
    log = Util.configure_logging(name=__name__)
    file_path = "%s://%s:%s/%s/%s/%s" % (remote["scheme"], remote["url"], remote["port"], category, tag, filename)
    file_res = requests.get(file_path, stream=True)
    if file_res.status_code != 200:
        log.fatal("Get failed with response: %d" % file_res.status_code)
    else:
        with open(output if output else filename, 'wb') as f:
            total_length = file_res.headers.get('content-length')

            if total_length is None:  # no content length header
                f.write(file_res.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in file_res.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
            # lf.write(file_res.text.encode('utf-8'))