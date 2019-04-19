API client objects
==================

API client objects provide direct access to the `rerobots API
<https://help.rerobots.net/api.html>`_ with several useful features like mapping
returned data into other types.

Example
-------

.. highlight:: python

::

  import rerobots.api

  apic = rerobots.api.APIClient()

  wdeployments = apic.get_deployments()
  print(apic.get_deployment_info(wdeployments[0]))


Create a new client object
--------------------------

.. autoclass:: rerobots.api.APIClient

Workspace deployments
---------------------

.. automethod:: rerobots.api.APIClient.get_deployments
.. automethod:: rerobots.api.APIClient.get_deployment_info

Instance creation and management
--------------------------------

``APIClient`` objects provide methods for working with instances. All operations
are associated with an API token.

Note that classes presented in :doc:`instances` abstract some of the methods of
``APIClient`` and provide combined operations, e.g., copying a file to an
instance via ssh.

.. automethod:: rerobots.api.APIClient.get_instances
.. automethod:: rerobots.api.APIClient.get_instance_info
.. automethod:: rerobots.api.APIClient.request_instance
.. automethod:: rerobots.api.APIClient.get_vpn_newclient
.. automethod:: rerobots.api.APIClient.terminate_instance
