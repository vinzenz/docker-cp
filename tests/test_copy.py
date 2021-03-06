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
import unittest

from docker_copy.copy import BUFFER_SIZE, _checked_buffer_size


class TestCopy(unittest.TestCase):

    def test_checked_buffer_size(self):
        @_checked_buffer_size
        def fun(src, dst, size):
            self.assertEqual(size, BUFFER_SIZE)

if __name__ == '__main__':
    unittest.main()
