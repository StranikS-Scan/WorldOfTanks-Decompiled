# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/notification/decorators.py
from helpers import dependency
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController

class HBProgressionLockButtonDecorator(MessageDecorator):
    _HBProgressionController = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(HBProgressionLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self._HBProgressionController.onSettingsChanged += self.__update

    def clear(self):
        self._HBProgressionController.onSettingsChanged -= self.__update
        super(HBProgressionLockButtonDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(HBProgressionLockButtonDecorator, self)._make(formatted, settings)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            if self._HBProgressionController.isEnabled:
                state = NOTIFICATION_BUTTON_STATE.DEFAULT
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
            buttonsStates = self._entity.get('buttonsStates')
            if buttonsStates is None:
                return
            buttonsStates['submit'] = state
            return

    def __update(self, *_):
        self.__updateEntityButtons()
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return
