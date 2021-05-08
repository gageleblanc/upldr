from botocore.exceptions import ClientError
from clilib.util.util import Util
from clilib.util.arg_tools import arg_tools
from upldr.upldr_libs.config_utils.loader import Loader
from pathlib import Path
import mimetypes
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
            "positionals": [],
            "subcommands": [
                {
                    "desc": "Upload file to S3",
                    "name": "put",
                    "positionals": [
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
                            "names": ["--content-type"],
                            "help": "Upload content type. Useful if you'd like to serve images.",
                            "required": False,
                            "default": False,
                            "type": str
                        },
                        {
                            "names": ["--acl"],
                            "help": "Upload ACL.",
                            "required": False,
                            "default": False,
                            "type": str
                        }
                    ]
                }
            ],
            "flags": [
                {
                    "names": ["--debug"],
                    "help": "Print additional debugging information.",
                    "required": False,
                    "default": False,
                    "action": "store_true"
                },
                {
                    "names": ["-b", "--bucket"],
                    "help": "Which S3 bucket to use. This is required if you don't have a default bucket set.",
                    "required": False,
                    "default": False,
                    "type": str
                }
            ]
        }
        args = arg_tools.build_nested_subparsers(self.spec)
        self.args = args
        self.log = Util.configure_logging(args, __name__)
        self.home = str(Path.home())
        self.config_dir = "%s/.config/upldr" % self.home
        self.config_path = "%s/.config/upldr/s3.json" % self.home
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)
        try:
            config_loader = Loader(self.config_path, auto_create=True, keys=['bucket', 'acl'])
            self.config = config_loader.get_config()
        except TypeError as type_error:
            self.log.fatal(type_error)
            exit(1)
        if self.args.bucket:
            self.config["bucket"] = self.args.bucket
        if self.args.acl:
            self.config["acl"] = self.args.acl
        self.log.debug(args)
        self.command_methods[args.subcmd]()

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
                    # if self._size == 0:
                    #     percentage = 0
                    # else:
                    #     percentage = (self._seen_so_far / self._size) * 100
                    sys.stdout.write(
                        "\rUploading [%s]: %s uploaded     " % (self._filename, convertSize(self._seen_so_far)))
                    sys.stdout.flush()

        # Upload the file
        s3_client = boto3.client('s3')
        try:
            if not self.args.content_type:
                self.log.debug("Guessing MimeType if not set by argument")
                self.args.content_type = mimetypes.MimeTypes().guess_type(self.args.source)[0]
            self.log.debug("Bucket:       %s" % self.config["bucket"])
            self.log.debug("Content Type: %s" % self.args.content_type)
            self.log.debug("ACL:          %s" % self.args.acl)
            self.log.debug("Category:     %s" % self.args.category)
            self.log.debug("Tag:          %s" % self.args.tag)
            self.log.info("Uploading %s to %s" % (file, object_name))
            response = s3_client.upload_file(self.args.source, self.config["bucket"], object_name,
                                             Callback=ProgressPercentage(file),
                                             ExtraArgs={'ContentType': self.args.content_type,
                                             'ACL': self.config["acl"]})
            print("\r\n", end="")
            self.log.debug(response)
            self.log.info("Upload Complete!")
        except ClientError as e:
            self.log.fatal(e)
            return False
        return True
