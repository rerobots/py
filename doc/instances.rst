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
