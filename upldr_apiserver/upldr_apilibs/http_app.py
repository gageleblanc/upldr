import os.path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from clilib.util.util import Util
from upldr_libs.serve import slave
from upldr_apilibs.index_data import IndexData
from pathlib import Path
from upldr_libs.config_utils.loader import Loader as ConfigLoader
from importlib.metadata import version
import platform
import json
import socket
import threading
import mimetypes


class HttpApp:
    @staticmethod
    def start_app(host="localhost", port=25565):
        logging = Util.configure_logging(__name__)
        server_address = (host, port)
        httpd = ThreadingHTTPServer(server_address, ServerObject)
        logging.info('Starting httpd...')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        logging.info('Stopping httpd...')


class ServerObject(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Server', 'UPLDR Apiserver v%s %s' % (version('upldr_apilibs'), platform.system()))
        self.end_headers()

    def _set_file_response(self, content_type, filename, content_length):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Content-Disposition', 'attachment; filename="%s"' % filename)
        self.send_header('Content-Length', content_length)
        self.send_header('Server', 'UPLDR Apiserver v%s %s' % (version('upldr_apilibs'), platform.system()))
        self.end_headers()

    def _not_found(self):
        self.send_error(404)
        self.send_header('Server', 'UPLDR Apiserver v%s %s' % (version('upldr_apilibs'), platform.system()))
        self.end_headers()
        self.wfile.write("File not found".encode('utf-8'))

    def do_GET(self):
        log = Util.configure_logging(name=__name__)
        log.info("GET path: |%s|" % self.path)
        if self.path != "/":
            path_parts = self.path.strip().split('/')
            log.info(path_parts)
            category = path_parts[1]
            tag = path_parts[2]
            file = path_parts[3]
            content_type = mimetypes.MimeTypes().guess_type(file)[0]
            config, destination = slave.slave_environment(category, tag, file)
            log.info("Serving file [%s]" % destination)
            try:
                with open(destination, 'rb') as f:
                    self._set_file_response(content_type, file, os.path.getsize(destination))
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self._not_found()
        else:
            log.info("Running index")
            IndexData()
            self._set_response()
            user_home = str(Path.home())
            upldr_config_dir = user_home + "/.config/upldr_apiserver"
            config_dir = Path(upldr_config_dir)
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = str(config_dir) + "/slave_config.json"
            config_loader = ConfigLoader(config=config_file, keys=["data_dir", "timeout", "host"], auto_create=True)
            config = config_loader.get_config()
            with open(config.data_dir + "/index.json") as f:
                data = json.load(f)
            self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_POST(self):
        log = Util.configure_logging(name=__name__)
        content_length = int(self.headers['Content-Length'])
        content_type = str(self.headers['Content-Type'])
        # print(content_length)
        post_data = self.rfile.read(content_length)
        if content_type == "application/json":
            parsed_data = json.loads(post_data.decode('utf-8'))
        else:
            log.warn("Bad request!")
            self._set_response()
            self.wfile.write(json.dumps({"Response": "Bad Request"}).encode('utf-8'))
            return
        log.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n" %
            (str(self.path), str(self.headers), parsed_data))
        log.info("Parsed Params: %s" % parsed_data)

        def free_port():
            free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            free_socket.bind(('0.0.0.0', 0))
            free_socket.listen(5)
            port = free_socket.getsockname()[1]
            free_socket.close()
            return port

        rand_port = free_port()
        self._set_response()
        self.wfile.write(json.dumps({"port": rand_port}).encode('utf-8'))
        category = parsed_data["category"]
        tag = parsed_data["tag"]
        if "\\" in parsed_data["filename"]:
            filename = parsed_data["filename"].split("\\")[-1]
        else:
            filename = parsed_data["filename"].split("/")[-1]
        port = rand_port

        config, destination = slave.slave_environment(category, tag, filename)
        threading.Thread(target=slave.run_standalone_native, args=(config.host, port, int(config.timeout), destination)).start()
