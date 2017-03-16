#!/usr/bin/env python

import os
import os.path
import tarfile

from contextlib import closing
from io import BytesIO

import docker
import docker.errors

from .error import ContainerNotFound, InvalidContainerSpec, ItemNotFound, \
    UsageError
from .tarstream import TarStream

BUFFER_SIZE = tarfile.RECORDSIZE


def _resolve_container(spec):
    """Resolves the container object, name and path from the spec argument.

    Raises ContainerNotFound when the container couldn't be found.
    """
    try:
        name, path = spec.split(':', 1)
    except ValueError:
        raise InvalidContainerSpec(
            '{0} is not a valid container spec.'.format(spec))

    try:
        return docker.from_env().containers.get(name), name, path
    except docker.errors.NotFound:
        raise ContainerNotFound(
            'Could not find a container "{0}"'.format(name))


def _get_archive(container, name, path):
    """ Retrieves an archive with the requested path from the container

    Raises ItemNotFound if the filesystem object could not be located inside
    the container.
    """
    try:
        return container.get_archive(path)
    except docker.errors.NotFound:
        raise ItemNotFound('No such file or directory {0} in the '
                           'container "{1}"'.format(path, name))


def copy_to_and_from_container(src, dst, buf_size=BUFFER_SIZE):
    """ Copies files/folders from the source container to the target container.

    Might raise UsageError, ItemNotFound and ContainerNotFound
    """

    src_container, src_name, src_path = _resolve_container(src)
    dst_container, dst_name, dst_path = _resolve_container(dst)

    src_archive, src_meta = _get_archive(src_container, src_name, src_path)
    with closing(src_archive):
        dst_container.put_archive(dst_path, src_archive)


def copy_from_container(src, dst, buf_size=BUFFER_SIZE):
    """ Copies a file/directory from the container and location specified in
    src to the directory location specified in dst

    Might raise UsageError, ItemNotFound and ContainerNotFound
    """

    src_container, src_name, src_path = _resolve_container(src)

    resource, metadata = _get_archive(src_container, src_name, src_path)

    with closing(resource) as r:
        archive = tarfile.open(fileobj=r, mode='r|*', bufsize=buf_size)
        with closing(archive) as a:
            for item in a:
                # Handle files only, since we need to buffer only files
                # all other things can be done by the original implementation
                if item.isreg():
                    if os.path.isfile(dst):
                        target = dst
                    else:
                        target = os.path.join(dst, item.name)
                    with open(target, 'wb') as dst_file:
                        blocks, left = divmod(item.size, buf_size)
                        for block in xrange(blocks):
                            tarfile.copyfileobj(a.fileobj, dst_file, buf_size)
                        if left > 0:
                            tarfile.copyfileobj(a.fileobj, dst_file, left)
                else:
                    # Let tarfile handle other things than files
                    a.extract(item, dst)


def copy_to_container(src, dst, buf_size=BUFFER_SIZE):
    """ Copies a file from src to the container and location specified in dst

    Might raise UsageError, ItemNotFound and ContainerNotFound
    """

    dst_container, dst_name, dst_path = _resolve_container(dst)
    if os.path.isfile(src):
        tfile = tarfile.open(
            fileobj=BytesIO(), mode='w|', bufsize=buf_size)
        info = tfile.gettarinfo(name=src, arcname=os.path.basename(src))
        header = info.tobuf()
        tfile.close()
        fstat = os.stat(src)
        with open(src, 'rb') as f:
            size = fstat.size
            padding_size = tarfile.BLOCKSIZE - (size % tarfile.BLOCKSIZE)
            padding_size += 2 * tarfile.BLOCKSIZE
            padding = padding_size * tarfile.NUL
            tstream = TarStream(header, f, size, padding, buf_size)
            dst_container.put_archive(dst_path, tstream)
    else:
        raise UsageError("Only files supported at this time")


def perform_copy(src, dst, buffer_length=None):
    """ Copies from src file/container to dst file/container using the
    appropriate implementation.

    Might raise UsageError, ItemNotFound and ContainerNotFound
    """
    f = None
    if ':' in src and ':' in dst:
        f = copy_to_and_from_container
    elif ':' in src:
        f = copy_from_container
    elif ':' in dst:
        f = copy_to_container
    else:
        raise UsageError('Neither source nor destination is a container.')

    print('Copying from {0} to {1} with buffer size {2}'
          .format(src, dst, buffer_length or 'N/A'))

    f(src, dst, buffer_length or BUFFER_SIZE)
