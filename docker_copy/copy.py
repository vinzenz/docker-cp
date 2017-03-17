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
import os
import os.path
import sys
import tarfile

from contextlib import closing
from functools import wraps

import docker
import docker.errors

from .bettertarstream import BetterTarStream
from .error import ContainerNotFound, InvalidContainerSpec, ItemNotFound, \
    UsageError

BUFFER_SIZE = tarfile.RECORDSIZE


def _checked_buffer_size(f):
    """ This decorator is used to ensure that the passed buffer size is
    always valid.
    """
    @wraps(f)
    def fun(src, dst, buffer_size=BUFFER_SIZE):
        if buffer_size <= 0:
            buffer_size = BUFFER_SIZE
        return f(src, dst, buffer_size)
    return fun


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


def _put_archive(container, name, path, stream):
    try:
        container.put_archive(path, stream)
    except docker.errors.NotFound:
        raise ItemNotFound(
            '{0} in container {1} could not be found'.format(path, name))


@_checked_buffer_size
def copy_to_stdout(src, _, buf_size=BUFFER_SIZE):
    src_container, src_name, src_path = _resolve_container(src)
    src_archive, src_meta = _get_archive(src_container, src_name, src_path)
    with closing(src_archive):
        tarfile.copyfileobj(src_archive, sys.stdout)


@_checked_buffer_size
def copy_from_stdout(_, dst, bufsize=BUFFER_SIZE):
    dst_container, dst_name, dst_path = _resolve_container(dst)
    _put_archive(dst_container, dst_name, dst_path, sys.stdin)


@_checked_buffer_size
def copy_from_and_to_container(src, dst, buf_size=BUFFER_SIZE):
    """ Copies files/folders from the source container to the target container.

    Might raise UsageError, ItemNotFound, ContainerNotFound
    """

    src_container, src_name, src_path = _resolve_container(src)
    dst_container, dst_name, dst_path = _resolve_container(dst)

    src_archive, src_meta = _get_archive(src_container, src_name, src_path)
    with closing(src_archive):
        _put_archive(dst_container, dst_name, dst_path, src_archive)


@_checked_buffer_size
def copy_from_container(src, dst, buf_size=BUFFER_SIZE):
    """ Copies a file/directory from the container and location specified in
    src to the directory location specified in dst

    Might raise UsageError, ItemNotFound, ContainerNotFound, OSError
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
                        # This is already a file on disc, so we will use it
                        target = dst
                    else:
                        # We're assuming this to be a directory instead
                        target = os.path.join(dst, item.name)

                    # Perform the actual copying
                    with open(target, 'wb') as dst_file:
                        # Calculate the number of blocks and the size of the
                        # last block (if not zero)
                        blocks, left = divmod(item.size, buf_size)
                        for _ in xrange(blocks):
                            tarfile.copyfileobj(a.fileobj, dst_file, buf_size)
                        if left:
                            tarfile.copyfileobj(a.fileobj, dst_file, left)
                else:
                    # Let tarfile handle other things than files
                    a.extract(item, dst)


@_checked_buffer_size
def copy_to_container(src, dst, buf_size=BUFFER_SIZE):
    """ Copies a file from src to the container and location specified in dst

    Might raise UsageError, ItemNotFound, ContainerNotFound, OSError
    """

    if not os.path.exists(src):
        raise ItemNotFound("{0} could not be found.".format(src))

    dst_container, dst_name, dst_path = _resolve_container(dst)
    _put_archive(dst_container, dst_name, dst_path,
                 BetterTarStream(buf_size, os.path.normpath(src)))


def perform_copy(src, dst, buffer_length=None):
    """ Copies from src file/container to dst file/container using the
    appropriate implementation.

    Might raise UsageError, ItemNotFound and ContainerNotFound
    """
    implementation = None
    if src is '-' and dst is not '-':
        implementation = copy_from_stdout
    elif dst is '-' and src is not '-':
        implementation = copy_to_stdout
    elif ':' in src and ':' in dst:
        implementation = copy_from_and_to_container
    elif ':' in src:
        implementation = copy_from_container
    elif ':' in dst:
        implementation = copy_to_container
    else:
        raise UsageError('Neither source nor destination is a container.')

    sys.stderr.write('Copying from {0} to {1} with buffer size {2}\n'
                     .format(src, dst, buffer_length or 'N/A'))

    implementation(src, dst, buffer_length or BUFFER_SIZE)
