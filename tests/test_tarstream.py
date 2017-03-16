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
import inspect
import os
import unittest

from docker_copy.tarstream import TarStream

SCRIPT_DIR = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
TEST_DATA_DIR = os.path.join(SCRIPT_DIR, 'data')


class TestTarStream(unittest.TestCase):

    def test_add_item_size_verifications(self):
        ts = TarStream(8, SCRIPT_DIR)
        ts.add_item('data')
        # Header
        #   512
        self.assertEqual(ts.tell(), 512)
        ts.add_item('data/file1.txt')
        # Header + Header + (File + padding)
        #   512  +  512   +      512
        self.assertEqual(ts.tell(), 1536)
        ts.finalize()
        # Header + Header + (File + padding) + finalization
        #   512  +  512   +      512         +     1024
        self.assertEqual(ts.tell(), 2560)
        ts.close()

    def test_applied_buffer_size8(self):
        ts = TarStream(8, SCRIPT_DIR)
        ts.finalize()
        # 1024 bytes => 128 * 8 bytes
        count = len([x for x in ts if len(x) == 8])
        self.assertEqual(count, 128)
        ts.close()

    def test_applied_buffer_size2(self):
        ts = TarStream(2, SCRIPT_DIR)
        ts.finalize()
        # 1024 bytes => 512 * 2 bytes
        count = len([x for x in ts if len(x) == 2])
        self.assertEqual(count, 512)
        ts.close()

if __name__ == '__main__':
    unittest.main()
