# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_hangar_widget.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_hangar_widget_model import RankedHangarWidgetModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
_R_SIMPLE_TOOLTIP = R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent()
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class RankedWidgetComponent(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def __init__(self):
        super(RankedWidgetComponent, self).__init__()
        self.__view = None
        return

    def _dispose(self):
        self.__view = None
        super(RankedWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = RankedWidget(flags=ViewFlags.VIEW)
        return self.__view


class RankedWidget(ViewImpl):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.ranked.RankedHangarWidget())
        settings.flags = flags
        settings.model = RankedHangarWidgetModel()
        super(RankedWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedWidget, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.RANKED_BATTLES_RANK:
                rankID = int(event.getArgument('rankID'))
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(rankID,))
            return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(None,))
        else:
            return super(RankedWidget, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return SimpleTooltipContent(contentID, event.getArgument('header', ''), event.getArgument('body', ''), event.getArgument('note', ''), event.getArgument('alert', '')) if contentID == _R_SIMPLE_TOOLTIP else None

    def _onLoading(self, *args, **kwargs):
        super(RankedWidget, self)._onLoading(*args, **kwargs)
        self.__fillRankedWidget()
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        super(RankedWidget, self)._finalize()

    def _update(self, *_, **__):
        self.__fillRankedWidget()

    @replaceNoneKwargsModel
    def __fillRankedWidget(self, model=None):
        currentRankID = self.__rankedController.getCurrentRank()[0]
        currentRank = self.__rankedController.getRank(currentRankID)
        model.setIsFinal(currentRank.isFinal())
        if currentRank.isFinal():
            statsComposer = self.__rankedController.getStatsComposer()
            prevWebSeasonInfo = self.__rankedController.getClientSeasonInfo()
            currWebSeasonInfo = self.__rankedController.getWebSeasonProvider().seasonInfo
            if currWebSeasonInfo.league == UNDEFINED_LEAGUE_ID:
                currWebSeasonInfo = prevWebSeasonInfo
            currLeagueID = currWebSeasonInfo.league
            currEfficiency = statsComposer.currentSeasonEfficiency.efficiency
            currEfficiencyDiff = statsComposer.currentSeasonEfficiencyDiff
            currPosition = currWebSeasonInfo.position
            model.setLeagueID(currLeagueID)
            if currEfficiency:
                model.setEfficiency(currEfficiency)
            if currEfficiencyDiff:
                model.setEfficiencyDiff(currEfficiencyDiff)
            if currPosition:
                model.setPosition(currPosition)
            model.setIsEfficiencyUnavailable(not currEfficiency)
            model.setIsPositionUnavailable(not currPosition)
            self.__fillRankData(model.rankRight, currentRank)
        else:
            nextRank = self.__rankedController.getRank(currentRankID + 1)
            model.setHasLeftRank(not currentRank.isInitialForNextDivision())
            if not currentRank.isInitialForNextDivision():
                self.__fillRankData(model.rankLeft, currentRank)
            self.__fillRankData(model.rankRight, nextRank)
            stepsCurrent = stepsTotal = 0
            progress = nextRank.getProgress()
            if progress is not None:
                steps = progress.getSteps()
                stepsTotal = len(steps)
                stepsCurrent = sum([ 1 for step in steps if step.isAcquired() ])
            model.setSteps(stepsCurrent)
            model.setStepsTotal(stepsTotal)
        bonusBattles = 0
        if self.__rankedController.getCurrentSeason():
            bonusBattles = self.__rankedController.getClientBonusBattlesCount()
        model.setBonusBattles(bonusBattles)
        clientMaxRankID, _ = self.__rankedController.getClientMaxRank()
        model.setMaxRank(clientMaxRankID)
        statsComposer = self.__rankedController.getStatsComposer()
        model.setBattlesTotal(statsComposer.amountBattles)
        return

    @staticmethod
    def __fillRankData(model, rank):
        model.setRankID(rank.getID())
        model.setRankName(rank.getUserName())
        model.setDivisionID(rank.getDivision().getID())
        model.setIsUnburnable(rank.isVisualUnburnable())

    def __addListeners(self):
        g_clientUpdateManager.addCallbacks({'stats.dossier': self._update})
        self.__rankedController.onGameModeStatusUpdated += self._update
        self.__rankedController.onUpdated += self._update
        self.__rankedController.onGameModeStatusTick += self._update
        self.__rankedController.getWebSeasonProvider().onInfoUpdated += self._update
        self.viewModel.onClick += self.__onClick

    def __removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__rankedController.onGameModeStatusUpdated -= self._update
        self.__rankedController.onUpdated -= self._update
        self.__rankedController.onGameModeStatusTick -= self._update
        self.__rankedController.getWebSeasonProvider().onInfoUpdated -= self._update
        self.viewModel.onClick -= self.__onClick

    @staticmethod
    def __onClick():
        event_dispatcher.showRankedProgressionWindow()
