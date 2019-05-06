Tutorial
========

This tutorial demonstrates how to work with client code. For the :doc:`cli`,
there is a different :ref:`tutorial <ssec:cli-example>`.

Begin by `getting an API token
<https://help.rerobots.net/webui.html#making-and-revoking-api-tokens>`_ (`from
the Web UI <https://rerobots.net/tokens>`_). There are several ways to make it
available to the client code. In this example, we assume that it is saved to a
file named ``jwt.txt``. Instantiate ``APIClient`` with this token::

  import rerobots.api

  with open('jwt.txt') as fp:
      apic = rerobots.api.APIClient(api_token=fp.read())

Get a list of all workspace deployments that involve "misty" (i.e., robots by
`Misty Robotics <https://www.mistyrobotics.com/>`_)::

  apic.get_deployments(query='misty')

yielding a list like ::

  ['f9a4e96f-a8f3-4b25-ae14-5ebdff63f8af',
   'f06c8740-02a0-48ec-bdde-69ff88b71afd']

The list you receive might be different, depending on availability of workspace
deployments. To get more information about one of them, call
``get_deployment_info()``, for example::

  apic.get_deployment_info('f06c8740-02a0-48ec-bdde-69ff88b71afd')

which will return a Python ``dict`` like ::

  {'icounter': 131,
   'supported_addons': ['cam', 'mistyproxy'],
   'region': 'us:cali',
   'queuelen': 1,
   'created': '2019-03-11 01:07:31.507302',
   'id': 'f06c8740-02a0-48ec-bdde-69ff88b71afd',
   'type': 'fixed_misty2fieldtrial',
   'type_version': 1}

To instantiate from `this workspace deployment`_, ::

  rri = rerobots.api.Instance(wdeployment_id='f06c8740-02a0-48ec-bdde-69ff88b71afd', apic=apic)

.. _`this workspace deployment`: https://rerobots.net/workspace/f06c8740-02a0-48ec-bdde-69ff88b71afd

Then, methods on ``rri`` will affect the instance just created. For example, to
get the status of the instance, call ``rri.get_status()``, which usually begins
with ``'INIT'`` (i.e., initializing).  The instance is ready for action when
``rri.get_status() == 'READY'``. For more information about it, call
``rri.get_details()`` to get a Python ``dict`` like ::

  {'type': 'fixed_misty2fieldtrial',
   'region': 'us:cali',
   'starttime': '2019-05-06 23:24:13.489577',
   'status': 'READY',
   'conn': {
     'type': 'sshtun',
     'ipv4': '147.75.69.207',
     'port': 2210,
     'hostkeys': ['ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBOT0UCbWfQBuGlY48FvrOQR76jxIWBPzD2XWTNSba1iqTgDIfC+pc8Mpi/0RW0zXW+HDBrx/+QYzMcsGnAAv46U= root@newc498']}}

Notice that the connection type is ``sshtun`` and that the above host keys
should be expected from hosts in the instance.

Finally, to stop using the instance and delete your data from it, ::

  rri.terminate()
