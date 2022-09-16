# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/notification/decorators.py
from fun_random.gui.feature.fun_random_helpers import getDisabledFunRandomTooltip
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationGuiSettings, NotificationPriorityLevel
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from messenger import g_settings
from notification.decorators import MessageDecorator
from notification.settings import NOTIFICATION_BUTTON_STATE
from skeletons.gui.game_control import IFunRandomController

class FunRandomButtonDecorator(MessageDecorator):
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    __STR_PATH = R.strings.fun_random.message.startEvent
    __TEMPLATE = 'FunRandomStarted'

    def __init__(self, entityId):
        super(FunRandomButtonDecorator, self).__init__(entityId, entity=g_settings.msgTemplates.format(self.__TEMPLATE, ctx={'text': backport.text(self.__STR_PATH.text())}, data={'buttonsStates': {'submit': self.__isActive()}}), settings=NotificationGuiSettings(isNotify=True, priorityLevel=NotificationPriorityLevel.MEDIUM))

    def _make(self, formatted=None, settings=None):
        self.__updateButtons()
        super(FunRandomButtonDecorator, self)._make(formatted, settings)

    def __updateButtons(self):
        if self._entity is None:
            return
        else:
            buttonsLayout = self._entity.get('buttonsLayout')
            buttonsStates = self._entity.get('buttonsStates')
            if not buttonsLayout or buttonsStates is None:
                return
            if self.__funRandomCtrl.isFunRandomPrbActive():
                state, tooltip = NOTIFICATION_BUTTON_STATE.HIDDEN, ''
            elif self.__isActive():
                state, tooltip = NOTIFICATION_BUTTON_STATE.DEFAULT, ''
            else:
                state = NOTIFICATION_BUTTON_STATE.VISIBLE
                tooltip = self.__getDisabledTooltip()
            buttonsStates['submit'] = state
            buttonsLayout[0]['tooltip'] = tooltip
            return

    def __isActive(self):
        return self.__funRandomCtrl.isAvailable() and self.__funRandomCtrl.canGoToMode()

    def __getDisabledTooltip(self):
        if self.__funRandomCtrl.isAvailable() and not self.__funRandomCtrl.canGoToMode():
            tooltipText = getDisabledFunRandomTooltip(self.__STR_PATH.disabledButton.noVehicles.tooltip())
        else:
            tooltipText = backport.text(self.__STR_PATH.disabledButton.disabledEvent.tooltip())
        return makeTooltip(body=tooltipText)
