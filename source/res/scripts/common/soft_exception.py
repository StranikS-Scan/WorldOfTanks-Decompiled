# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/soft_exception.py


class SoftException(Exception):
    pass


class DisabledServiceSoftException(SoftException):

    def __init__(self, message='disabledService'):
        super(DisabledServiceSoftException, self).__init__(message)
        self.message = message
