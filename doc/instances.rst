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

  import rerobots.api

  inst = rerobots.api.Instance(['fixed_misty2fieldtrial'])
  print(inst.get_status())


Create a new workspace instance
-------------------------------

.. autoclass:: rerobots.api.Instance


.. automethod:: rerobots.api.Instance.start_sshclient
.. automethod:: rerobots.api.Instance.exec_ssh
.. automethod:: rerobots.api.Instance.get_file
.. automethod:: rerobots.api.Instance.put_file
.. automethod:: rerobots.api.Instance.sftp_client
