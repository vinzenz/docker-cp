#!/usr/bin/env python

import os
import tarfile

from io import BytesIO


class TarStream(object):
    """ Implements a file like object for uploading a file in tar archive
    format, to a docker container via the docker library.
    This is implemented by using a fixed size buffer to avoid memory usage
    spikes. The maximum overhead of this class is 1024 bytes for the tar
    archive format.

    Cauton: This class is specialized on the usecase and the file API only
    returns what is necessary to fullfil `requests` needs on the API.
    """

    def __init__(self, buf_size, root_dir):
        """ Initializes a new TarStream object

        `buf_size` is the maximum buffer size to use.
        `root_dir` is the base directory for the fs items to add.
                   All paths for added items are supposed to be relative to
                   this one.
        """

        self._tfile = tarfile.open(fileobj=BytesIO(), bufsize=buf_size,
                                   mode='w|')
        self._root = root_dir
        self._chain = []
        self._entries = []
        self._cur = None
        self._buf_size = buf_size
        self._size = 0
        self._finalized = False
        self._read_bytes = 0

        if hasattr(os, 'lstat'):
            self._stat = os.lstat
        else:
            self._stat = os.stat

    def close(self):
        if self._cur:
            self._cur.close()
            self._cur = None
        if self._tfile:
            self._tfile.close()
            self._tfile = None

    def _get_padding(self, fsize):
        if fsize > 0:
            return tarfile.BLOCKSIZE - (fsize % tarfile.BLOCKSIZE)
        return 0

    def _calc_size(self, fsize):
        return tarfile.BLOCKSIZE + fsize + self._get_padding(fsize)

    def add_item(self, path):
        """ Add file system object specified in `path` to the tar file

        `path` needs to be relative to the root directory passed on class
        initialization
        """
        fpath = os.path.join(self._root, path)
        fsize = 0

        if os.path.isfile(fpath):
            # If it is a file, we need to know the file size
            stat = self._stat(fpath)
            fsize = stat.st_size

        self._entries += [(path, fsize)]
        self._size += self._calc_size(fsize)

    def finalize(self):
        if self._finalized:
            raise RuntimeError("Already finalized")
        self._finalized = True

        # Adding finalization indicator number of NULs.
        size = tarfile.BLOCKSIZE * 2
        self._entries += [(None, size)]
        self._size += size

        if (self._size % tarfile.BLOCKSIZE) != 0:
            raise RuntimeError(
                'TarStream not aligned: size = {0}'.format(self._size))

        self._chain_next()

    def tell(self):
        """ Returns always just the size"""
        return self._size

    def seek(self, off, direction):
        """ Won't do anything since `requests` would just jump to the end and
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
        if self._cur is None:
            raise StopIteration()

        buf = bytes()

        # Explanation of the following loop:
        # While there is not enough data in buf and the chain is not empty,
        # read 0 to block_size bytes from the first element in the chain.
        # When the the element hit the end, pop it from the list and continue
        # unless the list is empty which will break the loop and we'll exit

        while len(buf) < self._buf_size and self._cur:
            rsize = self._buf_size - len(buf)
            rbuf = self._cur.read(rsize)
            buf += rbuf
            if len(rbuf) < rsize:
                self._chain_next()
        self._read_bytes += len(buf)
        return buf

    def _chain_next(self):

        # if there's currently a file stream open we release it
        if self._cur:
            self._cur.close()
            self._cur = None

        if self._chain:
            # Are there more file streams prepared? If so use them first.
            self._cur = self._chain.pop(0)
        elif self._entries:
            # No more prepared streams, lets continue preparing.
            name, size = self._entries.pop(0)
            if name is None:
                # We're at the end. Adding tarfile finalizer.
                self._cur = BytesIO(size * tarfile.NUL)
                self._chain = []
            else:
                # Create tar header stream, open file stream (if is file) and
                # add a padding stream (for files only as well)
                path = os.path.join(self._root, name)
                info = self._tfile.gettarinfo(path, name)
                self._cur = BytesIO(info.tobuf())
                if info.isreg():
                    padding = self._get_padding(size)
                    self._chain += [open(path, 'rb'),
                                    BytesIO(padding * tarfile.NUL)]
