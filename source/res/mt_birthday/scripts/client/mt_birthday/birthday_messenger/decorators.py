# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_messenger/decorators.py
from datetime import timedelta, datetime
from gui.shared.notifications import NotificationGuiSettings, NotificationPriorityLevel, NotificationGroup
from messenger import g_settings
from mt_birthday.birthday_constants import GFNotificationTemplates
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_TYPE

class BirthdayGiftCustomMessageDecorator(MessageDecorator):
    _VIEW_TIMEOUT = 6000
    _TEMPLATE = GFNotificationTemplates.CUSTOM_BIRTHDAY_GIFT_NOTIFICATION

    def __init__(self, entityID, lootboxID, count, newCount, model=None):
        self.__count = count
        self.__incrCount = newCount
        self.__lootboxID = lootboxID
        entity = self.__makeEntity()
        settings = NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.MEDIUM, lifeTime=self._VIEW_TIMEOUT, groupID=NotificationGroup.INVITE)
        super(BirthdayGiftCustomMessageDecorator, self).__init__(entityID, entity, settings, model=model)

    def getPriorityLevel(self):
        return super(BirthdayGiftCustomMessageDecorator, self).getPriorityLevel() if self.__incrCount > 0 else NotificationPriorityLevel.LOW

    def getType(self):
        return NOTIFICATION_TYPE.BIRTHDAY_GIFT

    def updateCount(self, count, newCount):
        self.__count = count
        self.__updateIncr(newCount)
        self._entity = self.__makeEntity()

    def addCount(self, count):
        self.__count += count
        self.__updateIncr(count)
        self._entity = self.__makeEntity()

    def setLootBoxID(self, lootboxID):
        self.__lootboxID = lootboxID

    def resetCount(self):
        self.__count = 0
        self.__incrCount = 0
        self._entity = self.__makeEntity()

    def __makeEntity(self):
        self.__updatedTime = datetime.utcnow()
        return g_settings.msgTemplates.format(self._TEMPLATE, data={'linkageData': {'lootboxID': self.__lootboxID,
                         'count': self.__count,
                         'incrCount': self.__incrCount}})

    def __updateIncr(self, count):
        if self.__updatedTime + timedelta(milliseconds=self._VIEW_TIMEOUT) >= datetime.utcnow():
            self._settings.lifeTime += (datetime.utcnow() - self.__updatedTime).total_seconds() * 1000
            self.__incrCount += count
        else:
            self._settings.lifeTime = self._VIEW_TIMEOUT
            self.__incrCount = count


class BirthdayBonusMessageDecorator(BirthdayGiftCustomMessageDecorator):
    _TEMPLATE = GFNotificationTemplates.CUSTOM_BIRTHDAY_BONUS_NOTIFICATION

    def getType(self):
        return NOTIFICATION_TYPE.BIRTHDAY_BONUS
