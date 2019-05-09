Command-line interface
======================

Summary
-------

The command-line interface (CLI) is self-documenting. To begin, try::

  rerobots help

which will result in a message similar to the following

.. highlight:: none

::

  usage: rerobots [-h] [-V] [-t FILE]
                  {info,list,search,wdinfo,launch,terminate,version,help} ...

  rerobots API command-line client

  positional arguments:
    {info,list,search,wdinfo,launch,terminate,version,help}
      info                print summary about instance.
      list                list all instances owned by this user.
      search              search for matching deployments. empty query implies
			  show all existing workspace deployments.
      wdinfo              print summary about workspace deployment.
      launch              launch instance from specified workspace deployment or
			  type. if none is specified, then randomly select from
			  those available.
      terminate           terminate instance.
      version             print version number and exit.
      help                print this help message and exit

  optional arguments:
    -h, --help            print this help message and exit
    -V, --version         print version number and exit.
    -t FILE, --jwt FILE   plaintext file containing API token; with this flag,
			  the REROBOTS_API_TOKEN environment variable is
			  ignored.

Call ``help`` to learn more about commands, e.g., ``rerobots help info`` to
learn usage of ``rerobots info``.

To use an `API token <https://rerobots.net/tokens>`_, assign it to the
environment variable ``REROBOTS_API_TOKEN``, or give it through a file named in
the command-line switch ``-t``.


.. _ssec:cli-example:

Example
-------

Search for workspace deployments.

.. highlight:: none

::

  $ rerobots search
  f06c8740-02a0-48ec-bdde-69ff88b71afd



.. highlight:: none

::

  $ rerobots wdinfo f06c8740-02a0-48ec-bdde-69ff88b71afd
  {
    "icounter": 87,
    "supported_addons": [
      "cam",
      "mistyproxy"
    ],
    "region": "us:cali",
    "queuelen": 0,
    "desc": "",
    "created": "2019-03-11 01:07:31.507302",
    "id": "f06c8740-02a0-48ec-bdde-69ff88b71afd",
    "type": "fixed_misty2fieldtrial",
    "type_version": 1
  }

.. highlight:: none

::

  $ rerobots launch f06c8740-02a0-48ec-bdde-69ff88b71afd
  instance 94b3aec9-3c72-41dd-bedb-52f0a2b0f078
  writing secret key for ssh access to file key.pem...

.. highlight:: none

::

  $ rerobots info 94b3aec9-3c72-41dd-bedb-52f0a2b0f078
  {
    "region": "us:cali",
    "status": "READY",
    "deployment": "f06c8740-02a0-48ec-bdde-69ff88b71afd",
    "rootuser": "scott",
    "starttime": "2019-04-29 16:23:08.939807",
    "hostkeys": [
      "ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFXNjFWPS0247QzYf84xun3I6t8bgLnaeb9uKdomD/+WUh0+7CUFbdaSIYHR+3tPQinUAe/ExyqKiGezBqTzlo0= root@newc315"
    ],
    "id": "94b3aec9-3c72-41dd-bedb-52f0a2b0f078",
    "type": "fixed_misty2fieldtrial",
    "fwd": {
      "ipv4": "147.75.69.207",
      "port": 2210
    }
  }

``rerobots terminate 94b3aec9-3c72-41dd-bedb-52f0a2b0f078``
