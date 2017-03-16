#!/usr/bin/env python


class UsageError(Exception):
    """ Indicator for docker_copy usage errors """

    def __init__(self, message, *args, **kwargs):
        super(UsageError, self).__init__(message, *args, **kwargs)
        self.message = message


class InvalidContainerSpec(Exception):
    """ Used when the specification for a container had an invalid form  """

    def __init__(self, *args, **kwargs):
        super(UsageError, self).__init__(*args, **kwargs)


class ContainerNotFound(UsageError):
    """ Used when a container couldn't be found  """

    def __init__(self, *args, **kwargs):
        super(UsageError, self).__init__(*args, **kwargs)


class ItemNotFound(UsageError):
    """ Used when the filesystem item couldn't be found in the container  """

    def __init__(self, *args, **kwargs):
        super(UsageError, self).__init__(*args, **kwargs)
