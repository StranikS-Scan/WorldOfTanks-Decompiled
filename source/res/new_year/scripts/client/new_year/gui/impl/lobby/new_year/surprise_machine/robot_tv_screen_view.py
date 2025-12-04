# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/surprise_machine/robot_tv_screen_view.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_screen_view_model import RobotTvScreenViewModel, RobotTvScreenState, RobotTvButtons
from new_year.skeletons.new_year import INewYearSurpriseMachine, INewYearCurrencyController
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui_lootboxes.gui.bonuses.bonuses_packers import getRewardsBonusPacker
from new_year.gui.shared.ny_machine_helper import stripOpenedLootboxTokens
from gui.server_events.bonuses import getNonQuestBonuses
from new_year.ny_constants import NyBtnTypes
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from helpers import dependency
from gui.impl.gen import R

class RobotTvScreenView(ViewImpl):
    __slots__ = ('__state',)
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.new_year.lobby.new_year.RobotTvScreenView(), model=RobotTvScreenViewModel())
        self.__state = None
        super(RobotTvScreenView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(RobotTvScreenView, self).getViewModel()

    def fillReward(self, bonuses):
        rewardsList = self.viewModel.getRewards()
        rewardsList.clear()
        cleaned = stripOpenedLootboxTokens(bonuses)
        rewards = []
        for bonusType, bonusValue in cleaned.iteritems():
            rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        packBonusModelAndTooltipData(rewards, rewardsList, packer=getRewardsBonusPacker())
        rewardsList.invalidate()

    def selectButton(self, btnType):
        if btnType == NyBtnTypes.LEFT:
            self.viewModel.setSelectedButton(RobotTvButtons.ONE)
        else:
            self.viewModel.setSelectedButton(RobotTvButtons.NOT_ONE)

    def _onLoading(self, *args, **kwargs):
        super(RobotTvScreenView, self)._onLoading(*args, **kwargs)
        self.__updateState(RobotTvScreenState.IDLE)
        self.viewModel.setTokensCount(self.__nyCurrencyController.getGiftMachineTokenCount)

    def _getEvents(self):
        return ((self.__nyCurrencyController.onCurrencyUpdated, self.__onCurrencyUpdated), (self.__nyMachineController.onStateUpdate, self.__updateState))

    def __updateState(self, state):
        if self.__state == state:
            return
        self.__state = state
        self.viewModel.setScreenState(state)

    def __onCurrencyUpdated(self, currency, count):
        if currency == NyCurrencyType.NYGIFTMACHINETOKEN:
            self.viewModel.setTokensCount(count)
