# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/notification/decorators.py
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import hasAvailableWeeklyQuestsOfferGiftTokens
from gui.shared.notifications import NotificationGroup, NotificationGuiSettings
from helpers import dependency
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache

class Comp7BondEquipmentDecorator(MessageDecorator):
    __itemsCache = dependency.descriptor(IItemsCache)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, entityID, notificationType, savedData, model, template, priority, useCounterOnce=True, isNotify=True):
        self.__notificationType = notificationType
        self.__useCounterOnce = useCounterOnce
        entity = g_settings.msgTemplates.format(template, ctx={'title': savedData['title']})
        settings = NotificationGuiSettings(isNotify=isNotify, priorityLevel=priority, groupID=self.getGroup())
        super(Comp7BondEquipmentDecorator, self).__init__(entityID, entity=entity, settings=settings, model=model)
        self.__itemsCache.onSyncCompleted += self.__onItemsSyncCompleted

    def getType(self):
        return self.__notificationType

    def getGroup(self):
        return NotificationGroup.OFFER

    def getSavedData(self):
        return self._entity.get('linkageData')

    def isShouldCountOnlyOnce(self):
        return self.__useCounterOnce

    @staticmethod
    def isPinned():
        return True

    def clear(self):
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        super(Comp7BondEquipmentDecorator, self).clear()

    def _make(self, entity=None, settings=None):
        self.__updateEntityButtons()
        super(Comp7BondEquipmentDecorator, self)._make(entity, settings)

    def __onItemsSyncCompleted(self, *_):
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            state = self.__getButtonState()
            self._entity.setdefault('buttonsStates', {}).update({'submit': state})
            return

    def __getButtonState(self):
        state = NOTIFICATION_BUTTON_STATE.VISIBLE
        if hasAvailableWeeklyQuestsOfferGiftTokens():
            state |= NOTIFICATION_BUTTON_STATE.ENABLED
        return state
