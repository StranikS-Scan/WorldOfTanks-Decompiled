# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/notification/decorators.py
from gui.shared.notifications import NotificationGuiSettings, NotificationGroup
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_TYPE

class RewardAvailableDecorator(MessageDecorator):
    _LIFETIME_IN_MS = 30000

    def __init__(self, entityID, savedData, model, template, priority):
        entity = g_settings.msgTemplates.format(template, data={'linkageData': savedData})
        settings = NotificationGuiSettings(isNotify=True, priorityLevel=priority, groupID=self.getGroup(), lifeTime=self._LIFETIME_IN_MS)
        super(RewardAvailableDecorator, self).__init__(entityID, entity=entity, settings=settings, model=model)

    def getType(self):
        return NOTIFICATION_TYPE.OTG_REWARD_AVAILABLE

    def getSavedData(self):
        return self._entity.get('linkageData')

    def isShouldCountOnlyOnce(self):
        return True

    def getGroup(self):
        return NotificationGroup.OFFER

    @staticmethod
    def isPinned():
        return True
