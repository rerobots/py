Workspace instances
===================

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
