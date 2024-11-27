# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/surprise_machine/robot_tv_screen_view.py
from constants import LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import getNonQuestBonuses
from gui_lootboxes.gui.bonuses.bonuses_packers import getRewardsBonusPacker
from helpers import dependency
from new_year.gui.impl.gen.view_models.common.ny_currency_type_model import NyCurrencyType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.robot_tv_screen_view_model import RobotTvScreenViewModel, RobotTvScreenState
from new_year.gui.shared.ny_currency_provider import NyCurrencyProvider
from new_year.skeletons.new_year import INewYearSurpriseMachine

class RobotTvScreenView(ViewImpl):
    __slots__ = ('__state', '__currencyProvider')
    __nyMachineController = dependency.descriptor(INewYearSurpriseMachine)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.new_year.lobby.new_year.RobotTvScreenView())
        settings.model = RobotTvScreenViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__state = None
        self.__currencyProvider = NyCurrencyProvider()
        super(RobotTvScreenView, self).__init__(settings)
        return

    def _initialize(self, *args, **kwargs):
        super(RobotTvScreenView, self)._initialize()
        self.__currencyProvider.initialize()

    def _finalize(self):
        self.__currencyProvider.finalize()
        super(RobotTvScreenView, self)._finalize()

    @property
    def viewModel(self):
        return super(RobotTvScreenView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RobotTvScreenView, self)._onLoading(*args, **kwargs)
        self.updateState(RobotTvScreenState.IDLE)
        with self.viewModel.transaction() as tx:
            tx.setTokensCount(self.__currencyProvider.getCurrencyCount(NyCurrencyType.NYGIFTMACHINETOKEN))

    def _getEvents(self):
        return ((self.__currencyProvider.onCurrencyUpdated, self.__onNyCoinsUpdate), (self.__nyMachineController.onStateUpdate, self.updateState))

    @replaceNoneKwargsModel
    def updateState(self, state, model=None):
        if self.__state == state:
            return
        self.__state = state
        model.setScreenState(state)

    @replaceNoneKwargsModel
    def __onNyCoinsUpdate(self, currency, count, model=None):
        if currency == NyCurrencyType.NYGIFTMACHINETOKEN:
            model.setTokensCount(count)

    @replaceNoneKwargsModel
    def fillReward(self, bonuses, model=None):
        rewardsList = model.getRewards()
        rewardsList.clear()
        rewards = []
        self.__removeUnnecessaryInfo(bonuses)
        for bonusType, bonusValue in bonuses.items():
            rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        packBonusModelAndTooltipData(rewards, rewardsList, packer=getRewardsBonusPacker())
        rewardsList.invalidate()

    def __removeUnnecessaryInfo(self, bonus):
        for token, value in bonus.get('tokens', {}).items():
            if token.startswith(LOOTBOX_TOKEN_PREFIX) and value.get('count') < 0:
                bonus['tokens'].pop(token)
