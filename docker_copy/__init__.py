#!/usr/bin/env python
from __future__ import print_function

import argparse
import sys

from .copy import BUFFER_SIZE, perform_copy
from .error import UsageError


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
        parser.print_help()
        return 1
    return 0

if __name__ == '__main__':
    main()
