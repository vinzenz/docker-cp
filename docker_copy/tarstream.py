#!/usr/bin/env python

import tarfile

from io import BytesIO


class TarStream(object):
    """ Implements a file like object for uploading a file in tar archive
    format to a docker container via the docker API. The whole thing by using
    a fixed size buffer for the file upload.

    This class is specialized on the usecase and the file API only returns
    what is necessary to fulfil requests needs on the API.
    """

    def __init__(self, header, stream, ssize, padding, block_size):
        self._chain = [BytesIO(header), stream, BytesIO(padding)]
        self._block_size = block_size
        self._size = len(header) + ssize + len(padding)
        if (self._size % tarfile.BLOCKSIZE) != 0:
            raise RuntimeError(
                'TarStream not aligned: size = {0}'.format(self._size))

    def tell(self):
        """ Returns always just the size"""
        return self._size

    def seek(self, off, direction):
        """ Won't do anything since requests would just jump to the end and
        the start to get the size of the file like object
        """
        return

    def __iter__(self):
        """ Comply with the iterator interface """
        return self

    def __next__(self):
        """ Comply with the iterator interface (python 3) """
        return self.next()

    def next(self):
        """ Comply with the iterator interface return max block_size bytes """

        # We're done when the chain is empty
        if not self._chain:
            raise StopIteration()

        buf = bytes()

        # Explanation of the following loop:
        # While there is not enough and the chain is not empty read 0 to
        # block_size bytes from the first element in the chain.
        # When the the element hit the end, pop it from the list and continue
        # unless the list is empty which will break the loop and we'll exit
        while len(buf) < self._block_size and self._chain:
            rsize = self._block_size - len(buf)
            rbuf = self._chain[0].read(rsize)
            buf += rbuf
            if len(rbuf) < rsize:
                self._chain.pop(0)
        return buf
