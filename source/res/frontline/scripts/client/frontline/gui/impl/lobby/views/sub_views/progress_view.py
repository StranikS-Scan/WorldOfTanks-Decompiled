# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/sub_views/progress_view.py
from helpers import dependency
from frameworks.wulf import ViewFlags, ViewSettings
from frontline.gui.frontline_bonus_packers import packBonusModelAndTooltipData
from frontline.gui.frontline_helpers import geFrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.progress_view_model import ProgressViewModel
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyVehiclesUrl
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showShop, closeFrontlineContainerWindow
from skeletons.gui.game_control import IEpicBattleMetaGameController
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons
from uilogging.epic_battle.loggers import EpicBattleLogger

class ProgressView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__tooltipItems', '__frontlineLevel', '__frontlineProgress', '__maxLevel', '__uiEpicBattleLogger')

    def __init__(self, layoutID=R.views.frontline.lobby.ProgressView(), **kwargs):
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, ProgressViewModel())
        settings.kwargs = kwargs
        self.__tooltipItems = {}
        self.__frontlineLevel, self.__frontlineProgress = self.__epicController.getPlayerLevelInfo()
        self.__maxLevel = self.__epicController.getMaxPlayerLevel()
        self.__uiEpicBattleLogger = EpicBattleLogger()
        super(ProgressView, self).__init__(settings)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipItems.get(tooltipId)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ProgressView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return None

    @property
    def viewModel(self):
        return super(ProgressView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ProgressView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self):
        with self.viewModel.transaction() as tx:
            nextLevelExp = self.__epicController.getPointsProgressForLevel(self.__frontlineLevel)
            tx.setLevel(self.__frontlineLevel)
            tx.setIsMaxLevel(self.__frontlineLevel == self.__maxLevel)
            tx.setNeededPoints(nextLevelExp)
            tx.setCurrentPoints(self.__frontlineProgress)
            self._updateFrontlineState(tx)

    def _updateFrontlineState(self, model):
        state, nextStateDate, secondsToState = geFrontlineState()
        model.setPendingDate(int(nextStateDate))
        model.setCountdownSeconds(secondsToState)
        model.setFrontlineState(state.value)
        isActive = state is FrontlineState.ACTIVE or state is FrontlineState.FROZEN
        model.setIsShopBannerVisible(isActive and self.__epicController.hasVehiclesToRent())
        if isActive:
            bonuses = self.__epicController.getLevelRewards(self.__frontlineLevel + 1)
            rewards = model.getRewards()
            packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipItems)

    def _getEvents(self):
        return ((self.viewModel.onShopClick, self.__onShopClick), (self.__epicController.onUpdated, self.__onEpicUpdated), (self.__epicController.onEventEnded, self.__onEventEnded))

    def __onShopClick(self):
        self.__uiEpicBattleLogger.log(EpicBattleLogActions.CLICK.value, item=EpicBattleLogButtons.SHOP.value, parentScreen=EpicBattleLogKeys.PROGRESS_VIEW.value)
        showShop(getBuyVehiclesUrl())
        closeFrontlineContainerWindow()

    def __onEventEnded(self):
        self.__frontlineLevel, self.__frontlineProgress = self.__epicController.getPlayerLevelInfo()
        self._fillModel()

    def __onEpicUpdated(self, diff):
        if 'metaLevel' in diff:
            newLevel, newProgress = diff['metaLevel']
            if newLevel is not self.__frontlineLevel or newProgress is not self.__frontlineProgress:
                self.__frontlineLevel = newLevel
                self.__frontlineProgress = newProgress
                self._fillModel()
        if 'seasons' in diff:
            with self.viewModel.transaction() as tx:
                self._updateFrontlineState(tx)
