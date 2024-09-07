# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/notification/decorators.py
from helpers import dependency
from gui.shared.notifications import NotificationGroup, NotificationGuiSettings, NotificationPriorityLevel
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE, NOTIFICATION_TYPE
from skeletons.gui.game_control import IWinbackController

class WinbackProgressionLockButtonDecorator(MessageDecorator):
    __winbackController = dependency.descriptor(IWinbackController)

    def __init__(self, entityID, entity=None, settings=None, model=None):
        self.__isProgressionSwitched = False
        super(WinbackProgressionLockButtonDecorator, self).__init__(entityID, entity, settings, model)
        self.__winbackController.winbackProgression.onSettingsChanged += self.__update
        self.__winbackController.winbackProgression.onGiftTokenUpdated += self.__update

    def clear(self):
        self.__winbackController.winbackProgression.onSettingsChanged -= self.__update
        self.__winbackController.winbackProgression.onGiftTokenUpdated -= self.__update
        super(WinbackProgressionLockButtonDecorator, self).clear()

    def _make(self, formatted=None, settings=None):
        self.__updateEntityButtons()
        super(WinbackProgressionLockButtonDecorator, self)._make(formatted, settings)

    def __isOfferGiftsChoosen(self, buttonsLayout):
        return buttonsLayout[0]['action'] == 'openWinbackSelectableRewardView' and not self.__winbackController.hasWinbackOfferGiftToken()

    def __updateEntityButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            buttonsStates = self._entity.get('buttonsStates')
            if not buttonsLayout or buttonsStates is None:
                return
            if not self.__winbackController.winbackProgression.isEnabled or self.__isProgressionSwitched or self.__isOfferGiftsChoosen(buttonsLayout):
                state = NOTIFICATION_BUTTON_STATE.HIDDEN
            else:
                state = NOTIFICATION_BUTTON_STATE.DEFAULT
            buttonsStates['submit'] = state
            return

    def __update(self, isProgressionSwitched=False, *_):
        self.__isProgressionSwitched = self.__isProgressionSwitched or isProgressionSwitched
        if self._model is not None:
            self._model.updateNotification(self.getType(), self._entityID, self._entity, False)
        return


class WinbackSelectableRewardReminderDecorator(MessageDecorator):

    def __init__(self, entityID):
        super(WinbackSelectableRewardReminderDecorator, self).__init__(entityID, self.__makeEntity(), self.__makeSettings())

    def isShouldCountOnlyOnce(self):
        return True

    def getGroup(self):
        return NotificationGroup.OFFER

    def getType(self):
        return NOTIFICATION_TYPE.WINBACK_SELECTABLE_REWARD_AVAILABLE

    def __makeEntity(self):
        return g_settings.msgTemplates.format('WinbackSelectableRewardReminder')

    def __makeSettings(self):
        return NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.LOW)
