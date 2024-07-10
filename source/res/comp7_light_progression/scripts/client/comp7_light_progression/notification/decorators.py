# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/notification/decorators.py
from helpers import dependency
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE
from comp7_light_progression.skeletons.game_controller import IComp7LightProgressionOnTokensController

class Comp7LightProgressionLockButtonDecorator(MessageDecorator):
    _comp7LightProgressionController = dependency.descriptor(IComp7LightProgressionOnTokensController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        super(Comp7LightProgressionLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self._comp7LightProgressionController.onSettingsChanged += self.__update

    def clear(self):
        self._comp7LightProgressionController.onSettingsChanged -= self.__update
        super(Comp7LightProgressionLockButtonDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(Comp7LightProgressionLockButtonDecorator, self)._make(formatted, settings)

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            if not buttonsLayout:
                return
            if self._comp7LightProgressionController.isEnabled:
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
