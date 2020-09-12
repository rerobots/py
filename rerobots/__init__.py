"""command-line interface and Python client library for the rerobots API

For more documentation, go to https://rerobots-py.readthedocs.io/
"""
try:
    # pylint: disable=import-error
    from ._version import __version__
except ImportError:
    __version__ = '0.0.0.dev0+Unknown'


from .instances import Instance
