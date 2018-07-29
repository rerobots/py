Command-line interface
======================


.. highlight:: none
::

  usage: rerobots [-h] [-t FILE]
		  {info,list,search,launch,terminate,version,help} ...

  rerobots API command-line client

  positional arguments:
    {info,list,search,launch,terminate,version,help}
      info                print summary about instance.
      list                list all instances owned by this user.
      search              search for matching deployments. empty query implies
			  show all existing workspace deployments.
      launch              launch instance from specified workspace deployment or
			  type. if none is specified, then randomly select from
			  those available.
      terminate           terminate instance.
      version             print version number and exit.
      help                print this help message and exit

  optional arguments:
    -h, --help            show this help message and exit
    -t FILE, --jwt FILE   plaintext file containing API token
