# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/serial_enter_tab_view.py
from account_helpers.AccountSettings import AccountSettings, SESSION_PROGRESS_REWARDS_LAST_SEEN_STEP
from frameworks.wulf import ViewSettings
from helpers import dependency
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.serial_enter_tab_view_model import SerialEnterTabViewModel
from gui.impl.lobby.daily import DailyTabs
from gui.impl.lobby.daily.daily_quests_tab_view import DailyQuestTabBase
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import ISessionProgressRewardsController

class SerialEnterTabView(DailyQuestTabBase, ViewImpl):
    TAB_CONST = DailyTabs.SERIAL
    LAYOUT_ID = R.views.lobby.daily.SerialEnterTabView()
    __sessionProgressRewardsController = dependency.descriptor(ISessionProgressRewardsController)

    def __init__(self, layoutID=None):
        settings = ViewSettings(layoutID or self.LAYOUT_ID)
        settings.model = SerialEnterTabViewModel()
        super(SerialEnterTabView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SerialEnterTabView, self).getViewModel()

    def onTabSelected(self, tabIdx):
        if tabIdx == self.TAB_CONST:
            return
        AccountSettings.setSettings(SESSION_PROGRESS_REWARDS_LAST_SEEN_STEP, self.__sessionProgressRewardsController.currentStep)

    def _onLoading(self, *args, **kwargs):
        super(SerialEnterTabView, self)._onLoading()
        self._updateModel()

    def _updateModel(self):
        currentStep = self.__sessionProgressRewardsController.currentStep
        isRewardWasReceivedToday = self.__sessionProgressRewardsController.isRewardWasReceivedToday
        lastSeenStep = AccountSettings.getSettings(SESSION_PROGRESS_REWARDS_LAST_SEEN_STEP)
        isLastStageCompleted = currentStep > self.__sessionProgressRewardsController.finalStep
        if isRewardWasReceivedToday:
            isViewed = currentStep == lastSeenStep
        else:
            isViewed = isLastStageCompleted
        with self.viewModel.transaction() as tx:
            tx.setIsEnabled(self.__sessionProgressRewardsController.isAvailable)
            tx.setIsCompleted(isRewardWasReceivedToday or isLastStageCompleted)
            tx.setIsViewed(isViewed)
            tx.setIsFinal(isLastStageCompleted)

    def _getEvents(self):
        return ((self.__sessionProgressRewardsController.onDataUpdated, self.__onDataUpdated),)

    def __onDataUpdated(self):
        self._updateModel()
