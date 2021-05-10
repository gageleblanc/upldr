# UPLDR

upldr is a tool I created to quickly transfer larger files between boxes in my lab without using scp. It's not a groundbreaking tool by any means, and scp is definitely more secure. There's also a separate tool written in node that can be used with upldr (and upldr was written with in mind) that exposes an api and manages uploads and upload destinations on a remote server. I plan/ned on using this to manage media (photos, videos) quickly from my desktop to a storage server in my lab. If you want to use the api server and default java upload slave, you'll need to have nodejs and npm installed as well as java.

## Quick Start
The easiest way to get upldr is by running ```pip install upldr``` as long as your python path is in your path. Compatibility on windows hasn't been fully tested yet. If you find any issues please feel free to open issues on github. I am more than happy to look into them and try and fix them.

## Docs
upldr is pretty simple and only really has 4 main functions:
* put
* s3
* api
* remote

### put
Put is used to upload a file.
```bash
$ upldr put --help
usage: upldr put [-h] [--remote REMOTE] [-c CATEGORY] [-t TAG] [--timeout TIMEOUT] [--resume] [--debug] NAME

Handles uploads to non-cloud based remotes.

positional arguments:
  NAME                  Source file to upload

optional arguments:
  -h, --help            show this help message and exit
  --remote REMOTE       Name of remote to use
  -c CATEGORY, --category CATEGORY
                        Category for upload.
  -t TAG, --tag TAG     Tag for upload.
  --timeout TIMEOUT     Amount of time in seconds to wait before connecting to upload slave. Often there is a delay.
  --resume              Resume upload
  --debug               Debug output
```
The put command takes a positional argument of the filename you'd like to upload. Without any arguments, upldr will attempt to upload your file to the default remote specified in ~/.config/upldr/config.json with the category and tag of default. The -t/--tag argument works the same way and can be used to for a different tag than default.

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
$ upldr put file.txt --remote remote2
```

### s3
#### This subcommand requires boto3
The S3 subcommand does the same thing as put, but uses s3 instead of an upldr remote. You should configure an aws account in the same way you would configure the awscli before using this command.
```bash
$ upldr s3 --help
usage: upldr s3 [-h] [--debug] [-b BUCKET] {put} ...

Tools for managing upldr external libraries

optional arguments:
  -h, --help            show this help message and exit
  --debug               Print additional debugging information.
  -b BUCKET, --bucket BUCKET
                        Which S3 bucket to use. This is required if you don't have a default bucket set.

subcommands:
  Tools for managing upldr external libraries

  {put}
    put                 Upload file to S3
```

### api
The api subcommand handles running the apiserver to accept uploads and indexing. Currently indexing doesn't serve much purpose within upldr.
```bash
$ upldr api --help
usage: upldr api [-h] [-d] {serve,index} ...

Handles apiserver commands. This subcommand requires upldr_apiserver

optional arguments:
  -h, --help     show this help message and exit
  -d, --debug    Print extended debugging information.

subcommands:
  Handles apiserver commands. This subcommand requires upldr_apiserver

  {serve,index}
    serve        Serve API Server
    index        Index data directory for apiserver
```

### remote
The remote subcommand handles adding, removing, listing, and setting the default remote upload server.
```bash
$ upldr remote --help
usage: upldr remote [-h] [--debug] {add,remove,set-default,list} ...

Manages remote apiserver configurations.

optional arguments:
  -h, --help            show this help message and exit
  --debug               Local upload destination

subcommands:
  Manages remote apiserver configurations.

  {add,remove,set-default,list}
    add                 Add remote to config
    remove              Remove remote from config
    set-default         Set default remote to use
    list                List remotes
```

### Additional Notes
* Any released versions in the repository correspond to versions available on PyPi.