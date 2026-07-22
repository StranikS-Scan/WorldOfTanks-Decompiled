# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/notification/decorators.py
from helpers import dependency
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE
from skeletons.gui.game_control import ITankAcademyController
from skeletons.gui.shared import IItemsCache

class TankAcademyAwardsDecorator(MessageDecorator):
    __tankAcademyController = dependency.descriptor(ITankAcademyController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        self.__questID = settings.auxData.get('questID') if settings else None
        self.__isWithSelectableReward = settings.auxData.get('isWithSelectableReward', False)
        super(TankAcademyAwardsDecorator, self).__init__(entityID, entity, settings, model)
        self.__tankAcademyController.onFinish += self.__update
        self.__itemsCache.onSyncCompleted += self.__update
        return

    def clear(self):
        self.__tankAcademyController.onFinish -= self.__update
        self.__itemsCache.onSyncCompleted -= self.__update
        super(TankAcademyAwardsDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(TankAcademyAwardsDecorator, self)._make(formatted, settings)

    def __update(self, *_, **__):
        self.__updateEntityButtons()
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
            buttonsStates = self._entity.get('buttonsStates')
            state = self._getButtonState()
            buttonsStates['submit'] = state
            return

    def _getButtonState(self):
        if self.__isWithSelectableReward:
            if self.__tankAcademyController.hasUnobtainedDelayedRewards():
                return NOTIFICATION_BUTTON_STATE.DEFAULT
        elif not self.__tankAcademyController.isFinished():
            return NOTIFICATION_BUTTON_STATE.DEFAULT
        return NOTIFICATION_BUTTON_STATE.VISIBLE
