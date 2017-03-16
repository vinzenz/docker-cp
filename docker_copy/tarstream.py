#!/usr/bin/env python

import tarfile

from io import BytesIO


class TarStream(object):

    def __init__(self, header, stream, ssize, padding, block_size):
        self._chain = [BytesIO(header), stream, BytesIO(padding)]
        self._block_size = block_size
        self._size = len(header) + ssize + len(padding)
        if (self._size % tarfile.BLOCKSIZE) != 0:
            raise RuntimeError(
                'TarStream not aligned: size = {0}'.format(self._size))

    def tell(self):
        return self._size

    def seek(self, off, direction):
        return

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if not self._chain:
            raise StopIteration()
        buf = bytes()
        while len(buf) < self._block_size and self._chain:
            rsize = self._block_size - len(buf)
            rbuf = self._chain[0].read(rsize)
            buf += rbuf
            if len(rbuf) < rsize:
                self._chain.pop(0)
        return buf
