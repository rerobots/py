Workspace instances
===================

Classes presented in this section have methods for working with instances.  They
are built on the rerobots API, but some methods do not correspond directly to
rerobots API calls. In practice, ``Instance`` will provide everything needed for
working with a single workspace instance, without need for raw calls from
:doc:`apiclient`.

Example
-------

.. highlight:: python

::

  import rerobots

  inst = rerobots.Instance(['fixed_misty2'])
  print(inst.get_status())


.. _ssec:instance-class:

Instance class
--------------

.. autoclass:: rerobots.Instance
   :members: start_sshclient, exec_ssh, get_file, put_file, sftp_client
