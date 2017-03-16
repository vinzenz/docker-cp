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
from __future__ import print_function

import argparse
import sys

from .copy import BUFFER_SIZE, perform_copy
from .error import ContainerNotFound, ItemNotFound, UsageError


def main():
    parser = argparse.ArgumentParser(
        description='Copies files from and to containers')
    parser.add_argument('source', type=str, help='Source location')
    parser.add_argument('dest', type=str, help='Destination location')
    parser.add_argument('--buffer-length', metavar='N', type=int,
                        default=BUFFER_SIZE, required=False,
                        help='Restrict the size of the buffer used for '
                             'reading/writing files transfered to and from '
                             'docker containers')
    args = parser.parse_args()
    try:
        if args.source is None or args.dest is None:
            parser.print_help()
            return 1
        perform_copy(args.source, args.dest, args.buffer_length)
    except UsageError as e:
        sys.stderr.write('ERROR: {0}\n\n'.format(e.message))
        if not isinstance(e, (ItemNotFound, ContainerNotFound)):
            parser.print_help()
        return 1
    return 0

if __name__ == '__main__':
    main()
