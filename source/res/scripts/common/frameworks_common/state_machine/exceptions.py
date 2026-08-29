# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/frameworks_common/state_machine/exceptions.py
from __future__ import absolute_import
from soft_exception import SoftException

class NodeError(SoftException):
    pass


class TransitionError(SoftException):
    pass


class StateError(SoftException):
    pass


class StateMachineError(SoftException):
    pass
