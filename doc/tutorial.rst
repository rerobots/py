Tutorial
========

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

  apic.get_wdeployments(query='misty')

yielding a list like ::

  [{'id': '2c0873b5-1da1-46e6-9658-c40379774edf', 'type': 'fixed_misty2'},
   {'id': '3a65acd4-4aef-4ffc-b7f9-d50e48fc5541', 'type': 'basic_misty2fieldtrial'}]

The list you receive might be different, depending on availability of workspace
deployments. To get more information about one of them, call
``get_wdeployment_info()``, for example::

  apic.get_wdeployment_info('3a65acd4-4aef-4ffc-b7f9-d50e48fc5541')

which will return a Python ``dict`` like ::

  {'id': '3a65acd4-4aef-4ffc-b7f9-d50e48fc5541',
   'type': 'basic_misty2fieldtrial',
   'type_version': 1,
   'supported_addons': ['cam', 'mistyproxy', 'drive'],
   'desc': '',
   'region': 'us:cali',
   'icounter': 886,
   'created': '2019-07-28 23:26:16.983048',
   'queuelen': 0}

Notice that the field ``supported_addons`` includes ``cam``. Later in this
tutorial, the ``cam`` add-on is used to get images from cameras in the
workspace.

The :ref:`Instance class <ssec:instance-class>` can be used to instantiate from
`this workspace deployment`_::

  rri = rerobots.Instance(wdeployment_id='3a65acd4-4aef-4ffc-b7f9-d50e48fc5541', apic=apic)

.. _`this workspace deployment`: https://rerobots.net/workspace/3a65acd4-4aef-4ffc-b7f9-d50e48fc5541

Then, methods on ``rri`` will affect the instance just created. For example, to
get the status of the instance, call ``rri.get_status()``, which usually begins
with ``'INIT'`` (i.e., initializing).  The instance is ready for action when
``rri.get_status() == 'READY'``. For more information about it, call
``rri.get_details()`` to get a Python ``dict`` like ::

  {'type': 'basic_misty2fieldtrial',
   'region': 'us:cali',
   'starttime': '2020-05-23 02:12:16.984534',
   'status': 'READY',
   'conn': {
     'type': 'sshtun',
     'ipv4': '147.75.70.51',
     'port': 2210,
     'hostkeys': ['ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBOBfAaj/HSSl7oJZ+CXnzxFsXnGQZjBh1Djdm8s7V1fdgdiyJn0JrBxzt0pSdcy50JZW+9qc1Msl34YXUjn0mwU= root@newc247']}}

Notice that the connection type is ``sshtun`` and that the above host keys
should be expected from hosts in the instance.

Recall from earlier in this tutorial that the ``cam`` add-on is supported by the
workspace. Activate it by calling ::

  rri.activate_addon_cam()

and waiting until ``rri.status_addon_cam()`` indicates that it is ready. In
practice, activation is completed within several seconds. Then, use
:ref:`get_snapshot_cam() <ssec:apiclient-addon-cam>` to get an image and save it
in a `NumPy`_ `ndarray`_, and display it with `Matplotlib`_::

  import matplotlib.pyplot as plt
  import numpy as np

  res = rri.get_snapshot_cam(dformat='ndarray')

  plt.imshow(res['data'])
  plt.show()

The resulting figure should open in a separate window.

Though not as powerful as dedicated ``ssh`` command-line programs, the
:ref:`Instance class <ssec:instance-class>` provides methods for basic
operations over SSH. To begin, start an ssh client::

  rri.start_sshclient()

Then, arbitrary commands can be executed on the host in the instance via
:meth:`exec_ssh <rerobots.Instance.exec_ssh>`. For example, ::

  rri.exec_ssh('pwd')

will return the default path from which commands are executed. Files can be
uploaded and downloaded using :meth:`put_file <rerobots.Instance.put_file>`,
and :meth:`get_file <rerobots.Instance.get_file>`, respectively. For
example, to download the file ``/etc/hosts`` from the remote host::

  rri.get_file('/etc/hosts', 'hosts')

Finally, to stop using the instance and delete your data from it, ::

  rri.terminate()


.. _NumPy: https://www.numpy.org/
.. _ndarray: https://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.html
.. _Matplotlib: https://matplotlib.org/
