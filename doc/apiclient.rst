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

  wdeployments = apic.get_wdeployments()
  print(apic.get_wdeployment_info(wdeployments[0]['id']))


Create a new client object
--------------------------

.. autoclass:: rerobots.api.APIClient

Workspace deployments
---------------------

.. automethod:: rerobots.api.APIClient.get_wdeployments
.. automethod:: rerobots.api.APIClient.get_wdeployment_info

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


.. _ssec:apiclient-addon-cam:

add-on: cam
-----------

The ``cam`` add-on provides access to cameras in the workspace through the
rerobots API.

.. automethod:: rerobots.api.APIClient.get_snapshot_cam


.. _ssec:apiclient-addon-mistyproxy:

add-on: mistyproxy
------------------

The ``mistyproxy`` add-on provides proxies for the HTTP REST and WebSocket APIs
of Misty robots.

.. automethod:: rerobots.api.APIClient.activate_addon_mistyproxy
.. automethod:: rerobots.api.APIClient.status_addon_mistyproxy
.. automethod:: rerobots.api.APIClient.deactivate_addon_mistyproxy
