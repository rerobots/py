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
deployments.
