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
		  {info,isready,addon-cam,addon-mistyproxy,list,search,wdinfo,launch,terminate,version,help}
		  ...

  rerobots API command-line client

  positional arguments:
    {info,isready,addon-cam,addon-mistyproxy,list,search,wdinfo,launch,terminate,version,help}
      info                print summary about instance.
      isready             indicate whether instance is ready with exit code.
      addon-cam           get image via add-on `cam`
      addon-mistyproxy    get proxy URL via add-on `mistyproxy`
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

The following video demonstrates how to search for types of workspaces, request
an instance, and finally terminate it. The same example is also presented below
in text.

Before beginning, `get an API token
<https://help.rerobots.net/webui.html#making-and-revoking-api-tokens>`_ (`from
the Web UI <https://rerobots.net/tokens>`_). In this example, we assume that it
is saved to a file named ``jwt.txt``.

.. original video is hosted at https://asciinema.org/a/PMqssHq0EMDclOvc72IOfyEvL

.. raw:: html

  <script id="asciicast-PMqssHq0EMDclOvc72IOfyEvL" src="https://asciinema.org/a/PMqssHq0EMDclOvc72IOfyEvL.js" async></script>

.. highlight:: none

Search for workspace deployments::

  $ rerobots search misty
  f9a4e96f-a8f3-4b25-ae14-5ebdff63f8af    fixed_misty1devel
  f06c8740-02a0-48ec-bdde-69ff88b71afd    fixed_misty2fieldtrial

Get more information about one of them::

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

Notice that ``queuelen = 0``, i.e., this workspace deployment is available, and
requests to instantiate from it now are likely to succeed. To do so, ::

  $ rerobots launch f06c8740-02a0-48ec-bdde-69ff88b71afd
  94b3aec9-3c72-41dd-bedb-52f0a2b0f078

which will result in a secret key being written locally to the file ``key.pem``.
This key should be used for ssh connections, e.g., with commands of the form
``ssh -i key.pem``. Get information about the new instance::

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

Finally, terminate the instance::

  $ rerobots terminate 94b3aec9-3c72-41dd-bedb-52f0a2b0f078
