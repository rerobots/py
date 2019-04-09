API client objects
==================

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

.. automethod:: rerobots.api.APIClient.get_instances
.. automethod:: rerobots.api.APIClient.get_instance_info
.. automethod:: rerobots.api.APIClient.request_instance
.. automethod:: rerobots.api.APIClient.get_vpn_newclient
.. automethod:: rerobots.api.APIClient.terminate_instance
