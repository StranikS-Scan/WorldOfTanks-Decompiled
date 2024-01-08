# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/hangar/entry_point_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.gui.frontline_helpers import isHangarAvailable, geFrontlineState
from gui.impl.gen import R
from frontline.gui.impl.gen.view_models.views.lobby.views.banner_view_model import BannerViewModel, PerformanceRiskEnum
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from uilogging.epic_battle.constants import EpicBattleLogActions, EpicBattleLogButtons, EpicBattleLogKeys
from uilogging.epic_battle.loggers import EpicBattleLogger

class EpicBattlesEntryPointView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.frontline.lobby.BannerView())
        settings.flags = flags
        settings.model = BannerViewModel()
        self.__uiEpicBattleLogger = EpicBattleLogger()
        super(EpicBattlesEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EpicBattlesEntryPointView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick), (self.__epicController.onUpdated, self.__onUpdate), (self.__epicController.onGameModeStatusTick, self.__onUpdate))

    def _onLoading(self, *args, **kwargs):
        super(EpicBattlesEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        from entry_point import isEpicBattlesEntryPointAvailable
        if isEpicBattlesEntryPointAvailable():
            with self.viewModel.transaction() as tx:
                state, stateEndDate, _ = geFrontlineState(True)
                tx.setFrontlineState(state.value)
                tx.setPhaseEndDate(stateEndDate)
                tx.setRewardsCount(self.__epicController.getNotChosenRewardCount())
                tx.setPerformanceRisk(PerformanceRiskEnum(self.__epicController.getPerformanceGroup()))
        else:
            self.destroy()

    def __onUpdate(self, _=None):
        self.__updateViewModel()

    def __onClick(self):
        if isHangarAvailable():
            self.__epicController.selectEpicBattle()
        self.__epicController.showProgressionDuringSomeStates()
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, EpicBattleLogButtons.ENTRY_POINT.value, parentScreen=EpicBattleLogKeys.HANGAR.value)
