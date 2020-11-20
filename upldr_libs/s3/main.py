from botocore.exceptions import ClientError
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
import boto3
import math
import threading
import sys
import os

class main:
    def __init__(self):
        self.command_methods = {
            "put": self.s3_upload
        }
        self.spec = {
            "desc": "Tools for managing upldr external libraries",
            "name": "s3",
            "positionals": [
                {
                    "name": "command",
                    "metavar": "COMMAND",
                    "help": 'Supported subcommands are: {}'.format(", ".join(self.command_methods.keys())),
                    "default": "list",
                    "type": str
                },
                {
                    "name": "source",
                    "metavar": "SRC",
                    "help": "Source file to upload",
                    "default": False,
                    "type": str
                }
            ],
            "flags": [
                {
                    "names": ["-c", "--category"],
                    "help": "Upload category",
                    "required": False,
                    "default": "default",
                    "type": str
                },
                {
                    "names": ["-t", "--tag"],
                    "help": "Upload tag",
                    "required": False,
                    "default": "default",
                    "type": str
                },
                {
                    "names": ["--debug"],
                    "help": "Print additional debugging information.",
                    "required": False,
                    "default": False,
                    "type": bool,
                    "action": "store_true"
                }
            ]
        }
        args = arg_tools.build_full_subparser(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.log.debug(args)
        self.command_methods[args.command]()

    def s3_upload(self):
        file = self.args.source
        tag = self.args.tag
        category = self.args.category

        file_name = file.split(os.path.sep)[-1].replace(" ", "_")

        object_name = "{}/{}/{}".format(category, tag, file_name)

        self.log.debug("File Name (Raw): %s" % file)
        self.log.debug("File Name (Parsed): %s" % file_name)
        self.log.debug("Object Name: %s" % object_name)

        class ProgressPercentage(object):
            def __init__(self, filename):
                self._filename = filename
                # try:
                #     self._size = client.head_object(Bucket='upldr-s3', Key=object_name)["ContentLength"]
                # except Exception as _e:
                #     print(_e)
                self._size = 0
                self._seen_so_far = 0
                self._lock = threading.Lock()

            def __call__(self, bytes_amount):
                def convertSize(size):
                    if size == 0:
                        return '0B'
                    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
                    i = int(math.floor(math.log(size, 1024)))
                    p = math.pow(1024, i)
                    s = round(size / p, 2)
                    return '%.2f %s' % (s, size_name[i])

                # To simplify, assume this is hooked up to a single filename
                with self._lock:
                    self._seen_so_far += bytes_amount
                    if self._size == 0:
                        percentage = 0
                    else:
                        percentage = (self._seen_so_far / self._size) * 100
                    sys.stdout.write(
                        "\rUploading [%s]: %s uploaded     " % (self._filename, convertSize(self._seen_so_far)))
                    sys.stdout.flush()

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            self.log.info("Uploading %s to %s" % (file, object_name))
            response = s3_client.upload_file(self.args.source, 'upldr-s3', object_name, Callback=ProgressPercentage(file))
            print("\r\n", end="")
            self.log.info("Upload Complete!")
        except ClientError as e:
            self.log.fatal(e)
            return False
        return True
