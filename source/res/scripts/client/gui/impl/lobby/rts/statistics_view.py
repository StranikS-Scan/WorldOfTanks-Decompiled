# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/statistics_view.py
import logging
from RTSShared import RtsStats
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from skeletons.gui.shared import IItemsCache
from helpers import dependency
from gui.impl.gen import R
from constants import Configs
from skeletons.gui.lobby_context import ILobbyContext
from gui.impl.lobby.rts.rts_i_tab_view import ITabView
from gui.impl.gen.view_models.views.lobby.rts.meta_stats_view_model import MetaStatsViewModel
from gui.impl.gen.view_models.views.lobby.rts.meta_stats_card_model import MetaStatsCardModel, Submode
from gui.impl.gen.view_models.views.lobby.rts.meta_stat_indicator_model import MetaStatIndicatorModel, Indicator
from gui.impl.lobby.rts.tooltips.rts_points_tooltip_view import RTSPointsTooltipViewTanker, RTSPointsTooltipView1x7, RTSPointsTooltipView1x1
_logger = logging.getLogger(__name__)

class StatisticsView(ViewImpl, ITabView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MetaStatsViewModel()
        super(StatisticsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(StatisticsView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self._updateViewModel()

    def _finalize(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _updateViewModel(self):
        rts1x7Stats = self.__itemsCache.items.rtsStatistics.getRts1x7()
        rts1x1Stats = self.__itemsCache.items.rtsStatistics.getRts1x1()
        tankistStats = self.__itemsCache.items.rtsStatistics.getTankist()
        isRtsEnabled = self.__lobbyContext.getServerSettings().getRTSBattlesConfig().isStatisticsEnabled()
        with self.viewModel.transaction() as model:
            model.setIsEnabled(isRtsEnabled)
            if isRtsEnabled:
                cardsArray = model.getCards()
                cardsArray.clear()
                model1x7 = self.__createStatsCard(rts1x7Stats, Submode.ONEVSSEVEN)
                modelTanker = self.__createStatsCard(tankistStats, Submode.TANKER)
                model1x1 = self.__createStatsCard(rts1x1Stats, Submode.ONEVSONE)
                cardsArray.addViewModel(model1x1)
                cardsArray.addViewModel(modelTanker)
                cardsArray.addViewModel(model1x7)
                cardsArray.invalidate()

    def __createStatsCard(self, stats, mode):
        cardModel = MetaStatsCardModel()
        cardModel.setSubmode(mode)
        cardModel.setBattlesPlayed(stats[RtsStats.NUM_BATTLES])
        cardModel.setDamage(stats[RtsStats.AVERAGE_DAMAGE])
        array = cardModel.getStatIndicators()
        array.clear()
        self.__addIndicatorToArray(stats, RtsStats.LEADER_POINTS, Indicator.WINRATE, array, mode)
        if mode is Submode.TANKER:
            self.__addIndicatorToArray(stats, RtsStats.XP, Indicator.XP, array, mode)
            self.__addIndicatorToArray(stats, RtsStats.NUM_DESTROYED_TANKS, Indicator.TANKSDESTROYEDBYTANKER, array, mode)
            self.__addIndicatorToArray(stats, RtsStats.NUM_DESTROYED_SUPPLIES, Indicator.SUPPLIESDESTROYEDBYTANKER, array, mode)
        else:
            self.__addIndicatorToArray(stats, RtsStats.NUM_DESTROYED_TANKS, Indicator.TANKSDESTROYEDBYSTRATEGIST, array, mode)
            self.__addIndicatorToArray(stats, RtsStats.NUM_DESTROYED_TANKS_BY_SUPPLY, Indicator.TANKSDESTROYEDBYSTRATEGISTSUPPLIES, array, mode)
            self.__addIndicatorToArray(stats, RtsStats.AVERAGE_ACTIONS_PER_MINUTE, Indicator.AVGAPM, array, mode)
            self.__addIndicatorToArray(stats, RtsStats.PEAK_ACTIONS_PER_MINUTE, Indicator.PEAKAPM, array, mode)
        array.invalidate()
        return cardModel

    @staticmethod
    def __addIndicatorToArray(stats, statID, indicatorName, array, mode):
        if statID not in stats:
            _logger.warning('Missing stat [%s/%s] in RTS Statistics for mode %s.', statID, indicatorName, mode)
            value = -1
        else:
            value = stats[statID]
        model = MetaStatIndicatorModel()
        model.setType(indicatorName)
        model.setValue(value)
        array.addViewModel(model)

    def __onServerSettingsChange(self, serverSettingsDiff):
        if Configs.RTS_CONFIG.value in serverSettingsDiff:
            self._updateViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.rts.tooltips.RTSPointsTooltipView():
            submode = event.getArgument('submode')
            if submode == Submode.TANKER.value:
                return RTSPointsTooltipViewTanker()
            if submode == Submode.ONEVSONE.value:
                return RTSPointsTooltipView1x1()
            if submode == Submode.ONEVSSEVEN.value:
                return RTSPointsTooltipView1x7()
            _logger.warning('Submode has not referenced tooltipview: ' + str(submode))
        return None
