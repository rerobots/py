Command-line interface
======================

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
