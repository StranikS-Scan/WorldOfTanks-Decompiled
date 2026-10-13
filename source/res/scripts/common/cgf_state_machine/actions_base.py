# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_state_machine/actions_base.py
from __future__ import absolute_import
import abc
import logging
import CGF
from py2to3.patched_future import with_metaclass

class ActionBase(with_metaclass(abc.ABCMeta, object)):
    _DEV_ONLY = False
    _logger = logging.getLogger('CGFStateMachine')

    @classmethod
    def isDevOnly(cls):
        return cls._DEV_ONLY

    @classmethod
    def actionTypeName(cls):
        return cls.__name__

    @classmethod
    def actionDisplayName(cls):
        return cls.__name__

    @abc.abstractmethod
    def execute(self, gameObject):
        raise NotImplementedError
