from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from clilib.util.util import Util
from upldr_libs.serve import slave
import json
import socket
import threading


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
        self.end_headers()

    def do_GET(self):
        print("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        content_type = str(self.headers['Content-Type'])
        # print(content_length)
        post_data = self.rfile.read(content_length)
        if content_type == "application/json":
            parsed_data = json.loads(post_data.decode('utf-8'))
        else:
            print("Bad request!")
            self._set_response()
            self.wfile.write(json.dumps({"Response": "Bad Request"}).encode('utf-8'))
            return
        # print("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n" %
        #     (str(self.path), str(self.headers), parsed_data))
        # print("Parsed Params: %s" % parsed_data)

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
        filename = parsed_data["filename"]
        port = rand_port

        config, destination = slave.slave_environment(category, tag, filename)
        threading.Thread(target=slave.run_standalone_native, args=(config.host, port, int(config.timeout), destination)).start()
