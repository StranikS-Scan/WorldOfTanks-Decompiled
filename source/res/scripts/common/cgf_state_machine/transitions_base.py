# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_state_machine/transitions_base.py
from __future__ import absolute_import
import abc
import logging
from py2to3.patched_future import with_metaclass

class TransitionBase(with_metaclass(abc.ABCMeta, object)):
    _DEV_ONLY = False
    _logger = logging.getLogger('CGFStateMachine')

    @classmethod
    def isDevOnly(cls):
        return cls._DEV_ONLY

    @classmethod
    def transitionTypeName(cls):
        return cls.__name__

    @classmethod
    def transitionDisplayName(cls):
        return cls.__name__

    def activate(self):
        pass

    @abc.abstractmethod
    def update(self):
        return False
