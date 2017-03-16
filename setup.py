#!/usr/bin/env python
#
# Copyright 2017-present Vinzenz Feenstra
# Copyright 2017-present Red Hat, Inc. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Refer to the README and COPYING files for full details of the license.
#
from distutils.core import setup

setup(name='docker_copy',
      version='0.1',
      description='Copies files/folders from and to containers',
      author='Vinzenz Feenstra',
      author_email='evilissimo@redhat.com',
      url='https://github.com/vinzenz/docker-cp',
      packages=['docker_copy'],
      install_requires=['docker>=2.1.0'],
      entry_points={
          'console_scripts': ['docker-cp=docker_copy:main']})
