#!/usr/bin/env python

import os
import tarfile

from contextlib import closing
from io import BytesIO


class TarStream(object):
    """ Implements a tar stream from a path specified, providing at most
    `buf_size` big chunks.

    Caution: This class is specialized on the usecase and the file API only
    returns what is necessary to fullfil `requests` needs on the API.
    """

    def __init__(self, buf_size, path):
        """ Initializes a new TarStream object

        `buf_size` is the maximum buffer size to use.
        `path`     is the directory or file to create the tar stream from.
        """
        self._path = path
        self._buf_size = buf_size
        self._iterator = self._inner_next()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        return next(self._iterator)

    def _items(self):
        """ Generator to iterate over all files and folders to be added to
        the tar archive
        """
        # Handle the case of one file only
        if os.path.isfile(self._path):
            yield self._path, os.path.basename(self._path)
        else:
            src = os.path.normpath(self._path)
            src_prefix = os.path.dirname(src)
            for root, dirs, files in os.walk(src, topdown=True):
                rel_root = os.path.relpath(root, src_prefix)
                for name in dirs + files:
                    item = os.path.join(rel_root, name)
                    yield os.path.join(src_prefix, item), item

    def _inner_next(self):
        """ Generator that iterates over all streams and yields buffer chunks
        in the size of the buf_size parameter
        """
        for stream in self._streams():
            with closing(stream):
                while True:
                    buf = stream.read(self._buf_size)
                    if not buf:
                        break
                    yield buf

    def _streams(self):
        """ Generator that creates streams representing the tar format """
        tfile = tarfile.open(fileobj=BytesIO(), bufsize=self._buf_size,
                             mode='w|')
        with closing(tfile):
            for path, arcname in self._items():
                info = tfile.gettarinfo(path, arcname)
                # Yield the header as a stream
                yield BytesIO(info.tobuf())

                if info.isreg():
                    # Yield the file stream
                    yield open(path, 'rb')

                padding = info.size % tarfile.BLOCKSIZE
                if padding:
                    padding = tarfile.BLOCKSIZE - padding
                if padding:
                    # Yield the padding as a stream if necessary
                    yield BytesIO(padding * tarfile.NUL)

        # Yield the tar finalization marker
        yield BytesIO((tarfile.BLOCKSIZE * 2) * tarfile.NUL)
