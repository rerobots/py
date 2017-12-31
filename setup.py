# Copyright (C) 2017 rerobots, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from setuptools import setup


with open('README.rst') as fp:
    long_description = fp.read()


setup(name='rerobots',
      version='0.0.0.dev0',
      author='Scott C. Livingston',
      description='rerobots API command-line client',
      long_description=long_description,
      classifiers=['License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python :: 3.3',
                   'Programming Language :: Python :: 3.4',
                   'Programming Language :: Python :: 3.5'],
      packages=['rerobots'],
      install_requires=['requests'],
      entry_points={'console_scripts': ['rerobots = rerobots.cli:main']}
      )
