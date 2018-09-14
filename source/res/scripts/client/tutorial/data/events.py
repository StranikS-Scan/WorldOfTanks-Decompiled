# Embedded file name: scripts/client/tutorial/data/events.py
from tutorial.data.has_id import HasTargetID

class GUI_EVENT_TYPE(object):
    CLICK = 1
    CLICK_OUTSIDE = 2
    ESC = 3


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
        super(ClickEvent, self).__init__(GUI_EVENT_TYPE.CLICK, targetID)


class ClickOutsideEvent(_Event):

    def __init__(self, targetID):
        super(ClickOutsideEvent, self).__init__(GUI_EVENT_TYPE.CLICK_OUTSIDE, targetID)


class EscEvent(_Event):

    def __init__(self, targetID):
        super(EscEvent, self).__init__(GUI_EVENT_TYPE.ESC, targetID)
