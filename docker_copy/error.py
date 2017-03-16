#!/usr/bin/env python


class UsageError(Exception):

    def __init__(self, message, *args, **kwargs):
        super(UsageError, self).__init__(message, *args, **kwargs)
        self.message = message


class InvalidContainerSpec(Exception):

    def __init__(self, *args, **kwargs):
        super(UsageError, self).__init__(*args, **kwargs)


class ContainerNotFound(UsageError):

    def __init__(self, *args, **kwargs):
        super(UsageError, self).__init__(*args, **kwargs)


class ItemNotFound(UsageError):

    def __init__(self, *args, **kwargs):
        super(UsageError, self).__init__(*args, **kwargs)
