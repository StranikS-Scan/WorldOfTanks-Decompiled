# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale_progression/scripts/client/battle_royale_progression/notification/decorators.py
from helpers import dependency
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController

class BRProgressionLockButtonDecorator(MessageDecorator):
    _brProgressionController = dependency.descriptor(IBRProgressionOnTokensController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(BRProgressionLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self._brProgressionController.onSettingsChanged += self.__update

    def clear(self):
        self._brProgressionController.onSettingsChanged -= self.__update
        super(BRProgressionLockButtonDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(BRProgressionLockButtonDecorator, self)._make(formatted, settings)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            if self._brProgressionController.isEnabled:
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
