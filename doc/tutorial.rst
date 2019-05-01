Tutorial
========

This tutorial demonstrates how to work with client code. For the :doc:`cli`,
there is a different :ref:`tutorial <ssec:cli-example>`.

Begin by `getting an API token <https://rerobots.net/tokens>`_. Then,
instantiate a client object

.. highlight:: python

::

  import rerobots.api

  with open('path/to/jwt') as fp:
      apic = rerobots.api.APIClient(api_token=fp.read())
