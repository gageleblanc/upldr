from clilib.util.util import Util
from flask import Flask
import json


class ApiServer:
    def __init__(self, bind_addr="localhost", port=25565, data_dir="data", flat_db="db"):
        self.bind_addr = bind_addr
        self.port = port
        self.data_dir = data_dir
        self.flat_db_dir = flat_db

    def start_app(self):
        api = Flask(__name__)

        @api.route('/companies', methods=['GET'])
        def get_companies():
            return json.dumps(companies)