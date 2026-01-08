# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/seniority_awards/notifications/manual_claim_notification.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.seniority_awards.notifications.manual_claim_model import ManualClaimModel
from gui.impl.lobby.gf_notifications import NotificationBase
from helpers import dependency
from skeletons.gui.game_control import ISeniorityAwardsController
from uilogging.seniority_awards.constants import SeniorityAwardsLogSpaces
from uilogging.seniority_awards.loggers import RewardNotificationLogger

class ManualClaimNotification(NotificationBase):
    __seniorityAwardsController = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self, resId, *args, **kwargs):
        super(ManualClaimNotification, self).__init__(resId, ManualClaimModel(), *args, **kwargs)
        self.__uiRewardNotificationLogger = RewardNotificationLogger()

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        events = super(ManualClaimNotification, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick), (self.viewModel.onClose, self.__onClose))

    def _update(self):
        with self.viewModel.transaction() as tx:
            tx.setIsPopUp(self._isPopUp)

    def __onClick(self):
        displaySpace = SeniorityAwardsLogSpaces.HANGAR if self._isPopUp else SeniorityAwardsLogSpaces.NOTIFICATION_CENTER
        self.__uiRewardNotificationLogger.handleClickAction(displaySpace)
        self.__seniorityAwardsController.claimReward()

    def __onClose(self):
        self.destroyWindow()
