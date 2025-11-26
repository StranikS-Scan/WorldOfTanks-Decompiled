# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/banner_tooltip_view.py
from battle_royale.gui.constants import BattleRoyalePerfProblems, BattleRoyaleModeState
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.banner_tooltip_view_model import BannerTooltipViewModel, PerformanceRisk
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
PERFORMANCE_RISK_MAPPING = {BattleRoyalePerfProblems.HIGH_RISK: PerformanceRisk.HIGH,
 BattleRoyalePerfProblems.MEDIUM_RISK: PerformanceRisk.MEDIUM,
 BattleRoyalePerfProblems.LOW_RISK: PerformanceRisk.LOW}

class BannerTooltipView(ViewImpl):
    __battleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, modeState, *args, **kwargs):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.banner())
        settings.flags = ViewFlags.VIEW
        settings.model = BannerTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__modeState = modeState
        super(BannerTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BannerTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setPerformanceRisk(PERFORMANCE_RISK_MAPPING[self.__battleController.getPerformanceGroup()])
            tx.setModeState(self.__modeState)
            periodInfo = self.__battleController.getPeriodInfo()
            if not self.__battleController.isActive() or self.__battleController.getModeState() != BattleRoyaleModeState.Regular:
                timerValue = int(periodInfo.primeDelta)
            else:
                timerValue = self.__battleController.getTimeLeftTillCycleEnd()
            tx.setTime(timerValue)
