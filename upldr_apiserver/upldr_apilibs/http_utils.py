from clilib.util.util import Util
from urllib.parse import parse_qs


class HttpUtils:
    @staticmethod
    def get_query(q_string=None):
        if not q_string:
            log = Util.configure_logging(__name__)
            log.fatal("No query string provided.")
            exit(1)
        else:
            return parse_qs(q_string)