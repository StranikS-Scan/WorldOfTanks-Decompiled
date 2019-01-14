# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/transitions.py
import weakref
from .events import StateEvent, StringEvent
from .node import Node

class BaseTransition(Node):
    __slots__ = ('__targets', '__priority')

    def __init__(self, priority=0):
        super(BaseTransition, self).__init__()
        self.__targets = []
        self.__priority = priority

    def __repr__(self):
        return '{}({}->{}, priority={})'.format(self.__class__.__name__, self.getSource(), self.getTargets(), self.__priority)

    def clear(self):
        del self.__targets[:]
        super(BaseTransition, self).clear()

    def getPriority(self):
        return self.__priority

    def getSource(self):
        return self.getParent()

    def getTargets(self):
        return [ target() for target in self.__targets if target() is not None ]

    def setTarget(self, state):
        self.__targets.append(weakref.ref(state))

    def execute(self, event):
        raise NotImplementedError


class ConditionTransition(BaseTransition):
    __slots__ = ('__condition', '__invert')

    def __init__(self, condition, invert=False, priority=0):
        super(ConditionTransition, self).__init__(priority=priority)
        self.__condition = condition
        self.__invert = invert

    def clear(self):
        super(ConditionTransition, self).clear()
        self.__condition = None
        return

    def execute(self, event):
        result = self.__condition(event)
        if self.__invert:
            result = not result
        return result


class StringEventTransition(BaseTransition):
    __slots__ = ('__token',)

    def __init__(self, token='', priority=0):
        super(StringEventTransition, self).__init__(priority=priority)
        self.__token = token

    def execute(self, event):
        return not self.__token or event.token == self.__token if isinstance(event, StringEvent) else False
