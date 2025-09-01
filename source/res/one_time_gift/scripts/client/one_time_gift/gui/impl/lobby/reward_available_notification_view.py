# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/lobby/reward_available_notification_view.py
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from helpers import dependency, time_utils
from gui.impl.lobby.gf_notifications import NotificationBase
from one_time_gift.gui.impl.gen.view_models.views.lobby.reward_available_notification_view_model import RewardAvailableNotificationViewModel
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
TRAINING_FLAGS = FUNCTIONAL_FLAG.TRAINING | FUNCTIONAL_FLAG.EPIC_TRAINING

class RewardAvailableNotificationView(IGlobalListener, NotificationBase):
    __oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)

    def __init__(self, resId, *args, **kwargs):
        model = RewardAvailableNotificationViewModel()
        super(RewardAvailableNotificationView, self).__init__(resId, model, *args, **kwargs)

    @property
    def viewModel(self):
        return super(RewardAvailableNotificationView, self).getViewModel()

    def onPrbEntitySwitched(self):
        self._update()

    def onUnitPlayerRemoved(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.viewModel.setIsDisabled(False)

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.viewModel.setIsDisabled(pInfo.isReady)

    def _onLoading(self, *args, **kwargs):
        self.startGlobalListening()
        super(RewardAvailableNotificationView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.stopGlobalListening()
        super(RewardAvailableNotificationView, self)._finalize()

    def _getEvents(self):
        return super(RewardAvailableNotificationView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onClaimReward, self.__onClaimReward),
         (self.__oneTimeGiftController.onSettingsChanged, self._update),
         (self.__oneTimeGiftController.onEntryPointUpdated, self._update))

    def _update(self):
        with self.viewModel.transaction() as vm:
            vm.setIsPopUp(self._isPopUp)
            currentTime = time_utils.getServerUTCTime()
            if currentTime >= self.__oneTimeGiftController.getRemindTime():
                vm.setTimeLeft(self.__oneTimeGiftController.getEndTime() - currentTime)
            self.viewModel.setIsDisabled(self.__isButtonDisabled())

    def __onClose(self):
        self.destroyWindow()

    def __onClaimReward(self):
        self.__oneTimeGiftController.onEntryPointClicked()

    def __isButtonDisabled(self):
        if self.prbEntity and (self.prbEntity.isInQueue() or self.prbEntity.getModeFlags() & TRAINING_FLAGS):
            return True
        else:
            if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInUnit():
                if self.prbEntity and self.prbEntity.getPlayerInfo().isReady:
                    return True
            return False
