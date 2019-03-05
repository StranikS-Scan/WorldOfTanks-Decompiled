# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/data/events.py
from tutorial.data.has_id import HasTargetID
from shared_utils import CONST_CONTAINER

class GuiEventType(object):
    CLICK = 1
    CLICK_OUTSIDE = 2
    ESC = 3
    ENABLE = 4
    DISABLE = 5
    ENABLED_CHANGE = 6
    VISIBLE_CHANGE = 7


class _StateNames(CONST_CONTAINER):
    VISIBLE = 'visible'
    ENABLED = 'enabled'


class _Event(HasTargetID):

    def __init__(self, eventType, targetID):
        super(_Event, self).__init__(targetID=targetID)
        self.__eventType = eventType

    def getEventType(self):
        return self.__eventType

    def getActionCriteria(self):
        return (self.__eventType, self._targetID)


class ClickEvent(_Event):

    def __init__(self, targetID):
        super(ClickEvent, self).__init__(GuiEventType.CLICK, targetID)


class ClickOutsideEvent(_Event):

    def __init__(self, targetID):
        super(ClickOutsideEvent, self).__init__(GuiEventType.CLICK_OUTSIDE, targetID)


class EscEvent(_Event):

    def __init__(self, targetID):
        super(EscEvent, self).__init__(GuiEventType.ESC, targetID)


class EnableEvent(_Event):

    def __init__(self, targetID):
        super(EnableEvent, self).__init__(GuiEventType.ENABLE, targetID)


class DisableEvent(_Event):

    def __init__(self, targetID):
        super(DisableEvent, self).__init__(GuiEventType.DISABLE, targetID)


class EnabledChangeEvent(_Event):

    def __init__(self, targetID, state=False):
        super(EnabledChangeEvent, self).__init__(GuiEventType.ENABLED_CHANGE, targetID)
        self.__state = state

    def getStateValue(self):
        return self.__state

    def getStateName(self):
        return _StateNames.ENABLED


class VisibleChangeEvent(_Event):

    def __init__(self, targetID, state=False):
        super(VisibleChangeEvent, self).__init__(GuiEventType.VISIBLE_CHANGE, targetID)
        self.__state = state

    def getStateValue(self):
        return self.__state

    def getStateName(self):
        return _StateNames.VISIBLE
