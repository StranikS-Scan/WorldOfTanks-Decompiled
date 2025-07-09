# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/notifications.py
import logging
from constants import IS_DEVELOPMENT, NC_MESSAGE_PRIORITY
_logger = logging.getLogger(__name__)

class NotificationPriorityLevel(object):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    RANGE = (HIGH, MEDIUM, LOW)
    NC_MAPPING = {NC_MESSAGE_PRIORITY.HIGH: HIGH,
     NC_MESSAGE_PRIORITY.MEDIUM: MEDIUM,
     NC_MESSAGE_PRIORITY.LOW: LOW}

    @classmethod
    def convertFromNC(cls, priority):
        return cls.NC_MAPPING.get(priority, NotificationPriorityLevel.MEDIUM)


class NotificationGroup(object):
    INFO = 'info'
    INVITE = 'invite'
    OFFER = 'offer'
    ALL = (INFO, INVITE, OFFER)


class NotificationGuiSettings(object):
    __slots__ = ('isNotify', 'priorityLevel', 'isAlert', 'auxData', 'showAt', '__customEvent', 'groupID', 'messageType', 'messageSubtype', 'decorator', 'lifeTime')

    def __init__(self, isNotify=False, priorityLevel=NotificationPriorityLevel.MEDIUM, isAlert=False, auxData=None, showAt=0, groupID=NotificationGroup.INFO, messageType=None, messageSubtype=None, decorator=None, lifeTime=0):
        super(NotificationGuiSettings, self).__init__()
        self.isNotify = isNotify
        self.priorityLevel = priorityLevel
        self.isAlert = isAlert
        self.auxData = auxData or []
        self.showAt = showAt
        self.groupID = groupID
        self.messageType = messageType
        self.messageSubtype = messageSubtype
        self.decorator = decorator
        self.lifeTime = lifeTime
        self.__customEvent = None
        self.__validate()
        return

    def setCustomEvent(self, eType, ctx=None):
        self.__customEvent = (eType, ctx)

    def getCustomEvent(self):
        return self.__customEvent

    def __validate(self):
        if IS_DEVELOPMENT and self.priorityLevel not in NotificationPriorityLevel.RANGE:
            _logger.error('Invalid notification priority: %s', self.priorityLevel)
