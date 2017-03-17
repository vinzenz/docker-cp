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


class UsageError(Exception):
    """ Indicator for docker_copy usage errors """

    def __init__(self, message, *args, **kwargs):
        super(UsageError, self).__init__(message, *args, **kwargs)
        self.message = message


class InvalidContainerSpec(Exception):
    """ Used when the specification for a container had an invalid form  """

    def __init__(self, *args, **kwargs):
        super(InvalidContainerSpec, self).__init__(*args, **kwargs)


class ContainerNotFound(UsageError):
    """ Used when a container couldn't be found  """

    def __init__(self, *args, **kwargs):
        super(ContainerNotFound, self).__init__(*args, **kwargs)


class ItemNotFound(UsageError):
    """ Used when the filesystem item couldn't be found in the container  """

    def __init__(self, *args, **kwargs):
        super(ItemNotFound, self).__init__(*args, **kwargs)
