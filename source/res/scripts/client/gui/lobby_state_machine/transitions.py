# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/lobby_state_machine/transitions.py
from __future__ import absolute_import
import sys
from frameworks.state_machine import StateEvent, BaseTransition, State
from frameworks.state_machine.transitions import TransitionType
from gui.lobby_state_machine.events import _StopEvent
from gui.shared.events import NavigationEvent
from shared_utils import first

class NavigationTransition(BaseTransition):

    def __init__(self, transitionType=TransitionType.INTERNAL, record=False):
        super(NavigationTransition, self).__init__(transitionType=transitionType)
        self.record = record

    def execute(self, event):
        targetStateID = first(self.getTargets()).getStateID()
        return isinstance(event, NavigationEvent) and event.targetStateID == targetStateID

    def getPriority(self):
        return 1 if self.record else 0


class GuardTransition(NavigationTransition):

    def __init__(self, condition, transitionType=TransitionType.INTERNAL, record=False):
        super(GuardTransition, self).__init__(transitionType, record)
        self.condition = condition

    def getPriority(self):
        return sys.maxsize - 1

    def execute(self, event):
        if not isinstance(event, NavigationEvent) or isinstance(event, _StopEvent):
            return False
        else:
            parent = self.getSource()
            machine = parent.getMachine()
            target = first((state for state in machine.getRecursiveChildrenStates() if state.getStateID() == event.targetStateID), default=None)
            return super(GuardTransition, self).execute(event) if target and machine.findOwningSubtree(self.getSource()) is not machine.findOwningSubtree(target) else self.condition(event)


class HijackTransition(GuardTransition):

    def __init__(self, stateClazz, condition, transitionType=TransitionType.INTERNAL, record=False):
        super(HijackTransition, self).__init__(condition, transitionType, record)
        self.__stateCLazz = stateClazz

    def getPriority(self):
        return super(HijackTransition, self).getPriority() - 1

    def execute(self, event):
        return super(HijackTransition, self).execute(event) and event.targetStateID == self.__stateCLazz.STATE_ID


class _StopTransition(NavigationTransition):

    def getPriority(self):
        return sys.maxsize

    def execute(self, event):
        return isinstance(event, _StopEvent) and super(_StopTransition, self).execute(event)
