Introduction
============

Summary
-------

command-line interface and Python client library for the rerobots API

Releases are available `at PyPI <https://pypi.org/project/rerobots/>`_.

Documentation of the current release is at https://rerobots-py.readthedocs.io/
or can be built from sources as described below.


Getting started
---------------

To install the current release, try ::

   pip install rerobots

Besides installing the ``rerobots`` Python package, this will add the command
``rerobots`` to your shell. To get a brief help message, try ::

  rerobots help

Most interesting interactions with rerobots require an API token, which can be
provided through the environment variable ``REROBOTS_API_TOKEN`` or via the
command-line switch ``-t``.

For additional features, such as getting images from cameras as NumPy arrays, ::

  pip install rerobots[extra]


Testing and development
-----------------------

All tests are in the directory ``tests/``. If you have the ``rerobots`` package
installed, then you can ::

  make check

to run static analysis and tests that do not require a rerobots API token.
Recent results on `Travis CI <https://travis-ci.org/>`_ are available at
https://travis-ci.org/rerobots/py

Several other commands are available to run subsets of tests or create coverage
reports. For example, to run tests that do not touch production servers::

  make checklocal

and to measure code coverage: ``make checklocalcover``. To view the coverage
report, direct your Web browser at tests/cover/index.html

To build the User's Guide::

  make doc

and direct your Web browser at doc/build/index.html

There are extra tests (not run during ``make check``) that interact with
production servers in a way that requires an API token and that may cause
billing against the associated user account. These tests are only of interest if
you plan to contribute internal changes to this Python package.


Participating
-------------

All participation must follow our code of conduct, elaborated in the file
CODE_OF_CONDUCT.md in the same directory as this README.

Reporting errors, requesting features
`````````````````````````````````````

Please first check for prior reports that are similar or related in the issue
tracker at https://github.com/rerobots/py/issues
If your observations are indeed new, please `open a new
issue <https://github.com/rerobots/py/issues/new>`_

Reports of security flaws are given the highest priority and should be sent to
<security@rerobots.net>, optionally encrypted with the public key available at
https://rerobots.net/contact Please do so before opening a public issue to allow
us an opportunity to find a fix.

Contributing changes or new code
````````````````````````````````

Contributions are welcome! There is no formal declaration of code style. Just
try to follow the style and structure currently in the repository.

Contributors, who are not rerobots employees, must agree to the `Developer
Certificate of Origin <https://developercertificate.org/>`_. Your agreement is
indicated explicitly in commits by adding a Signed-off-by line with your real
name. (This can be done automatically using ``git commit --signoff``.)


License
-------

This is free software, released under the Apache License, Version 2.0.
You may obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
