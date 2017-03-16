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

from io import BytesIO

from docker_copy.tarstream import TarStream


class TestTarStream(unittest.TestCase):
    ALIGNED_PADDING = ('padding1' * 64)[12:]

    def test_init_raises_unaligned(self):
        with self.assertRaises(RuntimeError):
            TarStream('header', BytesIO(bytes('stream')), 6, 'padding', 6)

    def test_aligned_init(self):
        ts = TarStream('header', BytesIO(bytes('stream')), 6,
                       TestTarStream.ALIGNED_PADDING, 6)
        self.assertEqual(ts._size, 512)

    def test_tell_always_size(self):
        ts = TarStream('header', BytesIO(bytes('stream')), 6,
                       TestTarStream.ALIGNED_PADDING, 6)
        self.assertEqual(ts._size, ts.tell())
        ts.seek(0, 55)
        self.assertEqual(ts._size, ts.tell())

    def test_next_returns_buffer_size8(self):
        ts = TarStream('header', BytesIO(bytes('stream')), 6,
                       TestTarStream.ALIGNED_PADDING, 8)
        # Ensure that each item returned is 8 and that there are 64 entries
        # 8 * 64 = 512
        self.assertEqual(len([b for b in ts if len(b) == 8]), 64)


if __name__ == '__main__':
    unittest.main()
