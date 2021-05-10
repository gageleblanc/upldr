import socket
from pathlib import Path
from upldr_libs.config_utils.loader import Loader as ConfigLoader


def slave_environment(category, tag, filename):
    user_home = str(Path.home())
    upldr_config_dir = user_home + "/.config/upldr_apiserver"
    config_dir = Path(upldr_config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = str(config_dir) + "/slave_config.json"
    config_loader = ConfigLoader(config=config_file, keys=["data_dir", "timeout", "host"], auto_create=True)
    config = config_loader.get_config()
    parent_dir = "%s/%s/%s" % (config.data_dir, category, tag)
    Path(parent_dir).mkdir(parents=True, exist_ok=True)
    destination = "%s/%s/%s/%s" % (config.data_dir, category, tag, filename)
    return config, destination


def run_standalone_native(host, port, timeout, dest):
    # log = Util.configure_logging()
    print("begin standalone native")
    print("Starting native standalone upload slave on port %d and saving file to %s" % (port, dest))
    s = socket.socket()
    print("Binding to %s:%d" % (host, port))
    s.bind((host, int(port)))
    # if self.args.resume:
    #     f = open(self.args.destination, 'ab')
    #     if f.tell() > 1500:
    #         f.seek(-1500, 1)
    #     else:
    #         f.seek(0)
    #     self.log.info("Resuming upload from %d" % f.tell())
    # else:
    #     f = open(self.args.destination, 'wb')
    f = open(dest, 'wb')
    print("Listening with %d second timeout..." % timeout)
    s.settimeout(int(timeout))
    s.listen(5)
    try:
        c, addr = s.accept()
    except socket.timeout as ex:
        print("No clients connected before timeout. Exiting.")
        exit(1)
    print("Accepted connection")
    l = c.recv(8192)
    while l:
        f.write(l)
        l = c.recv(8192)
    f.close()
    print("Transfer complete")
    c.close()
    return
