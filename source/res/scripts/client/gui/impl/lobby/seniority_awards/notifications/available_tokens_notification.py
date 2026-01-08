# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/notifications/available_tokens_notification.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getPlayerSeniorityAwardsUrl
from gui.impl.gen.view_models.views.lobby.seniority_awards.notifications.available_tokens_model import AvailableTokensModel
from gui.impl.lobby.gf_notifications import NotificationBase
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from skeletons.gui.game_control import ISeniorityAwardsController
from uilogging.seniority_awards.constants import SeniorityAwardsLogSpaces
from uilogging.seniority_awards.loggers import CoinsNotificationLogger

class AvailableTokensNotification(NotificationBase):
    __seniorityAwardsController = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self, resId, *args, **kwargs):
        super(AvailableTokensNotification, self).__init__(resId, AvailableTokensModel(), *args, **kwargs)
        self.__uiCoinsNotificationLogger = CoinsNotificationLogger()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(AvailableTokensNotification, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick), (self.viewModel.onClose, self.__onClose))

    def _update(self):
        data = self._getPayload()
        with self.viewModel.transaction() as tx:
            tx.setIsPopUp(self._isPopUp)
            tx.setCount(data.get('count', 0))
            tx.setTimeLeft(data.get('timeLeft', 0))

    def __onClick(self):
        displaySpace = SeniorityAwardsLogSpaces.HANGAR if self._isPopUp else SeniorityAwardsLogSpaces.NOTIFICATION_CENTER
        self.__uiCoinsNotificationLogger.handleClickAction(displaySpace)
        showShop(getPlayerSeniorityAwardsUrl())

    def __onClose(self):
        self.destroyWindow()
