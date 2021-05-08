from upldr_apilibs.http_app import HttpApp


class ApiServer:
    def __init__(self, bind_addr="localhost", port=25565, data_dir="data", flat_db="db"):
        self.bind_addr = bind_addr
        self.port = port
        self.data_dir = data_dir
        self.flat_db_dir = flat_db
        self._start_app()

    def _start_app(self):
        HttpApp(host=self.bind_addr, port=self.port)
