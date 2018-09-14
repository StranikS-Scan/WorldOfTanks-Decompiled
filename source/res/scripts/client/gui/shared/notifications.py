# Embedded file name: scripts/client/gui/shared/notifications.py
from constants import NC_MESSAGE_PRIORITY

class NotificationPriorityLevel(object):
    HIGH = 'hight'
    MEDIUM = 'medium'
    LOW = 'low'
    RANGE = (HIGH, MEDIUM, LOW)
    NC_MAPPING = {NC_MESSAGE_PRIORITY.HIGH: HIGH,
     NC_MESSAGE_PRIORITY.MEDIUM: MEDIUM,
     NC_MESSAGE_PRIORITY.LOW: LOW}

    @classmethod
    def convertFromNC(cls, priority):
        result = NotificationPriorityLevel.MEDIUM
        if priority in cls.NC_MAPPING:
            result = cls.NC_MAPPING[priority]
        return result


class NotificationGuiSettings(object):
    __slots__ = ('isNotify', 'priorityLevel', 'isAlert', 'auxData', 'showAt', 'extraHandlerData')

    def __init__(self, isNotify = False, priorityLevel = NotificationPriorityLevel.MEDIUM, isAlert = False, auxData = None, showAt = 0):
        super(NotificationGuiSettings, self).__init__()
        self.isNotify = isNotify
        self.priorityLevel = priorityLevel
        self.isAlert = isAlert
        self.auxData = auxData or []
        self.showAt = showAt
        self.extraHandlerData = []
