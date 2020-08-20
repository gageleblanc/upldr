# UPLDR

upldr is a tool I created to quickly transfer larger files between boxes in my lab without using scp. It's not a groundbreaking tool by any means, and scp is definitely more secure. There's also a separate tool written in node that can be used with upldr (and upldr was written with in mind) that exposes an api and manages uploads and upload destinations on a remote server. I plan/ned on using this to manage media (photos, videos) quickly from my desktop to a storage server in my lab. If you want to use the api server and default java upload slave, you'll need to have nodejs and npm installed as well as java.

## Quick Start
The easiest way to get upldr is by running ```pip install upldr``` as long as your python path is in your path. Compatibility on windows hasn't been fully tested yet. If you find any issues please feel free to open issues on github. I am more than happy to look into them and try and fix them.

## Docs
upldr is pretty simple and only really has 4 main functions:
* libs
* put
* serve
* setup

### libs
The libs function handles external libraries that upldr can use. Currently, there's only really one external library and it's used to serve an api that manages uploads.
```bash
$ upldr libs --help
usage: upldr libs [-h] [--name NAME] command

Tools for managing upldr external libraries

positional arguments:
  command      Command to run.

optional arguments:
  -h, --help   show this help message and exit
  --name NAME  Library name

```
The only available commands for the libs function are install, delete, and list. Install will install all default external libs (only the one media-server-api lib gets installed right now) and catalog installed libs in ~/.config/upldr/libs.yaml. Delete will delete a lib from disk and the libs.yaml file. List dumps the contents of the libs.yaml file.

### put
Put is used to upload a file.
```bash
$ upldr put --help                                                                                                                                             (master) 
usage: upldr put [-h] [-r REMOTE] [-m] [--debug] [-p PORT] [-a REMOTE_HOST] [-c CATEGORY] [-t TAG] name

Uploads file to remote.

positional arguments:
  name                  Name of the file to be uploaded.

optional arguments:
  -h, --help            show this help message and exit
  -r REMOTE, --remote REMOTE
                        Name of the remote to use.
  -m, --manual          Don't hit api for socket
  --debug               Enable debug
  -p PORT, --port PORT  Port for manual mode
  -a REMOTE_HOST, --remote-host REMOTE_HOST
                        Remote host to use instead of configured remote
  -c CATEGORY, --category CATEGORY
                        Category for uploaded file
  -t TAG, --tag TAG     Tag for uploaded file
```
The put command takes a positional argument of the filename you'd like to upload. Without any arguments, upldr will attempt to upload your file to the default remote specified in ~/.config/upldr/remotes.yaml with the category and tag of default. If you don't want remotes or don't have any remotes configured yet, you can upload to standalone instances of the upload slave that are running with the -m flag. You can use the -a/--remote-host flag to specify the host of the slave and the --port flag to specify the port to connect to. You can use the -c/--category tag to specify a category other than default. The -t/--tag argument works the same way and can be used to for a different tag than default.

Example with remotes (default remote):
```bash
$ upldr put file.txt
```
Example with remotes, category, and tag (default remote):
```bash
$ upldr put file.txt -c text_files -t readmes
```
This will upload file.txt to <data_dir>/text_files/readmes/file.txt

Example with remotes (specified remote):
```bash
$ upldr put file.txt -r remote2
```
Example without remote:
```bash
$ upldr put file.txt -m -a remote2.foo -p 4444
```

### serve
Serve is used to start either the api server, a standalone java slave (the default for the api server), or a standalone python slave.
```bash
$ upldr serve --help 
usage: upldr serve [-h] [--destination DESTINATION] --port PORT mode

Starts an api server or standalone slave.

positional arguments:
  mode                  Server mode. This can be api or standalone

optional arguments:
  -h, --help            show this help message and exit
  --destination DESTINATION
                        Upload destination
  --port PORT           Port for slave to bind to
```
The two available mode are api and standalone. The api mode requires nodejs and java and will start a nodejs api server with the specified port. 
```bash
upldr serve standalone --native --help 
usage: upldr serve [-h] --destination DESTINATION --port PORT [--native] [--bind-addr BIND_ADDR] [--timeout TIMEOUT] mode

Starts an api server or standalone slave.

positional arguments:
  mode                  Server mode. This can be api or standalone

optional arguments:
  -h, --help            show this help message and exit
  --destination DESTINATION
                        Upload destination
  --port PORT           Port for slave to bind to
  --native              Use native python instead of java lib
  --bind-addr BIND_ADDR
                        Address for slave to bind to
  --timeout TIMEOUT     Time in seconds before server times out

```
The standalone mode by default will start a java slave with the specified port and destination. If run with the --native flag it will start a slave that runs in native python. Slaves started with the native flag can also set the timeout value of the slave. This tells the slave when to shut down if it has not recieved a connection.

### setup
The setup function handles setting up remotes.
```bash
$ upldr setup --help                                                                                                                                         (master) 
usage: upldr setup [-h] [-l] -n NAME [-u REMOTE_URL] [-s SCHEME] [-p PORT] [-t T] [--debug] [-a] [-r] [-d]

Sets up a remote for uploads. This can be specified in the upload command.

optional arguments:
  -h, --help            show this help message and exit
  -l                    List remotes
  -n NAME, --name NAME  Name of the remote to be added.
  -u REMOTE_URL, --remote-url REMOTE_URL
                        API Url for the remote.
  -s SCHEME, --scheme SCHEME
                        API scheme for the remote.
  -p PORT, --port PORT  API port for the remote.
  -t T                  Socket timeout
  --debug               Enable debug mode
  -a, --add             Add to config. This is the default action.
  -r, --delete          Delete from config.
  -d                    Set remote as default
```
Setup only takes flags as arguments. -n/--name will always refer to the name of the remote in context to what action you're preforming. You can delete remotes with -r/--delete. You can set a remote as default with -d. You can list your current remotes with -l and you can add a remote by specifying a name, scheme, url, and port without the delete flag. 