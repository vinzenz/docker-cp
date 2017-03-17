#!/usr/bin/env python

import os
import tarfile

from io import BytesIO


class BetterTarStream(object):
    """ Implements a file like object for uploading a file in tar archive
    format, to a docker container via the docker library.
    This is implemented by using a fixed size buffer to avoid memory usage
    spikes. The maximum overhead of this class is 1024 bytes for the tar
    archive format.

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
        for stream in self._streams():
            while True:
                buf = stream.read(self._buf_size)
                if not buf:
                    stream.close()
                    break
                yield buf
        yield bytes()

    def _streams(self):

        tfile = tarfile.open(fileobj=BytesIO(), bufsize=self._buf_size,
                             mode='w|')
        for path, arcname in self._items():
            info = tfile.gettarinfo(path, arcname)
            yield BytesIO(info.tobuf())

            if info.isreg():
                yield open(path, 'rb')

            padding = info.size % tarfile.BLOCKSIZE
            if padding:
                padding = tarfile.BLOCKSIZE - padding
            if padding:
                yield BytesIO(padding * tarfile.NUL)

        yield BytesIO((tarfile.BLOCKSIZE * 2) * tarfile.NUL)

        tfile.close()
