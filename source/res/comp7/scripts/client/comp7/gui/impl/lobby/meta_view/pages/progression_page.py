# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/meta_view/pages/progression_page.py
import logging
import typing
from functools import partial
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import COMP7_UI_SECTION, COMP7_PROGRESSION_PAGE_C11N_PROGRESS
from adisp import adisp_process
from comp7.gui.event_boards.event_boards_items import DailyVehicleData
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, MetaRootViews, Rank, SeasonName, StatisticsMode
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.customization_tasks_model import CustomizationTasksModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.day_statistics_model import DayStatisticsModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.top_vehicle_statistics_model import TopVehicleStatisticsModel
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_model import ProgressionItemModel
from comp7.gui.impl.gen.view_models.views.lobby.meta_view.pages.progression_model import ProgressionModel, PageState
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from comp7.gui.impl.lobby.comp7_helpers.comp7_c11n_helpers import getComp7ProgressionStyle, isC11nItemTokenAttainable, getVehicleForStyle, getMaxLevelAndBattlesVehicleSortKey, selectStyleAndDecalInC11nHangar
from gui.SystemMessages import pushMessage, SM_TYPE
from gui.impl.backport import text
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from comp7.gui.impl.lobby.comp7_helpers.comp7_gui_helpers import ProgressCacherUI
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import getDescriptionAndProgressFromC11nDecalQuest
from comp7.gui.impl.lobby.meta_view import meta_view_helper
from comp7.gui.impl.lobby.meta_view.pages import PageSubModelPresenter
from comp7.gui.impl.lobby.tooltips.day_tooltip import DayTooltip
from comp7.gui.impl.lobby.tooltips.rank_indicator_tooltip import RankIndicatorTooltip
from comp7.gui.impl.lobby.tooltips.battles_indicator_tooltip import BattlesIndicatorTooltip
from comp7.gui.impl.lobby.tooltips.wins_indicator_tooltip import WinsIndicatorTooltip
from comp7.gui.impl.lobby.tooltips.damage_indicator_tooltip import DamageIndicatorTooltip
from comp7.gui.impl.lobby.tooltips.prestige_indicator_tooltip import PrestigeIndicatorTooltip
from comp7.gui.impl.lobby.tooltips.division_tooltip import DivisionTooltip
from comp7.gui.impl.lobby.tooltips.fifth_rank_tooltip import FifthRankTooltip
from comp7.gui.impl.lobby.tooltips.general_rank_tooltip import GeneralRankTooltip
from comp7.gui.impl.lobby.tooltips.last_update_tooltip import LastUpdateTooltip
from comp7.gui.impl.lobby.tooltips.progression_table_tooltip import ProgressionTableTooltip
from comp7.gui.impl.lobby.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from comp7.gui.impl.lobby.tooltips.sixth_rank_tooltip import SixthRankTooltip
from comp7.gui.shared.event_dispatcher import showComp7MetaRootTab, showComp7SeasonVehiclesStatisticsView
from frameworks.wulf.view.array import fillViewModelsArray
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs
from gui.customization.constants import CustomizationModes
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from gui.shared.notifications import NotificationPriorityLevel as Priority
from gui.shared.utils.requesters import REQ_CRITERIA
from shared_utils import first
from skeletons.gui.customization import ICustomizationService
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
if typing.TYPE_CHECKING:
    from typing import List, Iterable, Tuple, Optional
    from comp7.gui.shared.gui_items.dossier.stats import AccountComp7StatsBlock
    from comp7.gui.shared.gui_items.dossier.stats import Comp7StatsBlock
    from comp7.gui.event_boards.event_boards_items import AggregatedDailyData, Comp7PlayerProgression, DailyData
    from comp7.helpers.comp7_server_settings import Comp7RanksConfig
    from gui.shared.gui_items.Vehicle import Vehicle
    CustData = Tuple[str, int, int, str, int, int, int]
_logger = logging.getLogger(__name__)

class ProgressionPage(PageSubModelPresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)
    __c11n = dependency.descriptor(ICustomizationService)

    def __init__(self, viewModel, parentView):
        super(ProgressionPage, self).__init__(viewModel, parentView)
        self.__lastUpdateTime = None
        self.__custProgQuestIDs = []
        self.__progressionData = None
        self.__selectedDayIndex = None
        self.__c11nProgressCacher = None
        return

    @property
    def pageId(self):
        return MetaRootViews.PROGRESSION

    @property
    def viewModel(self):
        return super(ProgressionPage, self).getViewModel()

    @property
    def ranksConfig(self):
        return self.__comp7Controller.getRanksConfig()

    def initialize(self, **params):
        super(ProgressionPage, self).initialize(**params)
        self.__updateData()
        self.__c11nProgressCacher = ProgressCacherUI(COMP7_UI_SECTION, COMP7_PROGRESSION_PAGE_C11N_PROGRESS, {})
        self.__updateCustomizationTasks()

    def finalize(self):
        self.__c11nProgressCacher.finalize()
        super(ProgressionPage, self).finalize()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == TOOLTIPS_CONSTANTS.SHOP_VEHICLE:
                vehicleCD = int(event.getArgument('vehicleCD'))
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(vehicleCD,))
            elif tooltipId == TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM and g_currentVehicle.item is not None:
                itemCD = int(event.getArgument('customizationId'))
                level = int(event.getArgument('progressionLevel'))
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=CustomizationTooltipContext(itemCD, -1, True, level))
            if tooltipData:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(ProgressionPage, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.lobby.tooltips.general_rank_tooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'divisions': event.getArgument('divisions'),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return GeneralRankTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.division_tooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'division': Division(event.getArgument('division')),
             'from': event.getArgument('from'),
             'to': event.getArgument('to')}
            return DivisionTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.progression_table_tooltip():
            return ProgressionTableTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.fifth_rank_tooltip():
            return FifthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.sixth_rank_tooltip():
            return SixthRankTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.rank_inactivity_tooltip():
            return RankInactivityTooltip()
        elif contentID == R.views.comp7.mono.lobby.tooltips.last_update_tooltip():
            description = event.getArgument('description')
            return LastUpdateTooltip(description=description, updateTime=self.__lastUpdateTime)
        elif contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView():
            vehicleCD = int(event.getArgument('vehicleCD'))
            return VehicleRolesTooltipView(vehicleCD)
        elif contentID == R.views.comp7.mono.lobby.tooltips.day_tooltip():
            rankValue = int(event.getArgument('rank') or 0)
            divisionValue = int(event.getArgument('division') or 0)
            rank = Rank(rankValue) if Rank.SIXTH <= rankValue <= Rank.FIRST else None
            division = Division(divisionValue) if Division.A <= divisionValue <= Division.E else None
            params = {'index': event.getArgument('index', 0),
             'isQualification': event.getArgument('isQualification', False),
             'hasBattles': event.getArgument('hasBattles', False),
             'seasonName': SeasonName(event.getArgument('seasonName')),
             'diff': event.getArgument('diff', 0),
             'rank': rank,
             'division': division,
             'ratingPoints': event.getArgument('ratingPoints', 0),
             'rankInactivityPenalty': event.getArgument('rankInactivityPenalty', 0),
             'currentDayIndex': event.getArgument('currentDayIndex', 0)}
            return DayTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.rank_indicator_tooltip():
            divisionValue = int(event.getArgument('division') or 0)
            division = Division(divisionValue) if Division.A <= divisionValue <= Division.E else None
            params = {'statisticsMode': StatisticsMode(event.getArgument('statisticsMode')),
             'rank': Rank(event.getArgument('rank')),
             'seasonName': SeasonName(event.getArgument('seasonName')),
             'maxAchievedRatingPoints': event.getArgument('maxAchievedRatingPoints'),
             'division': division,
             'ratingPoints': event.getArgument('ratingPoints'),
             'diff': event.getArgument('diff'),
             'dayOfMaxRatingIndex': event.getArgument('dayOfMaxRatingIndex')}
            return RankIndicatorTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.battles_indicator_tooltip():
            params = {'statisticsMode': StatisticsMode(event.getArgument('statisticsMode')),
             'soloBattlesCount': event.getArgument('soloBattlesCount'),
             'superPlatoonBattlesCount': event.getArgument('superPlatoonBattlesCount')}
            return BattlesIndicatorTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.wins_indicator_tooltip():
            params = {'statisticsMode': StatisticsMode(event.getArgument('statisticsMode')),
             'winRate': event.getArgument('winRate'),
             'winsCount': event.getArgument('winsCount'),
             'lossCount': event.getArgument('lossCount'),
             'drawCount': event.getArgument('drawCount')}
            return WinsIndicatorTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.damage_indicator_tooltip():
            params = {'statisticsMode': StatisticsMode(event.getArgument('statisticsMode')),
             'averageDamageDealt': event.getArgument('averageDamageDealt'),
             'recordDamageDealt': event.getArgument('recordDamageDealt'),
             'recordDamageDealtVehicleName': event.getArgument('recordDamageDealtVehicleName')}
            return DamageIndicatorTooltip(params=params)
        elif contentID == R.views.comp7.mono.lobby.tooltips.prestige_indicator_tooltip():
            params = {'statisticsMode': StatisticsMode(event.getArgument('statisticsMode')),
             'averagePrestige': event.getArgument('averagePrestige'),
             'recordPrestige': event.getArgument('recordPrestige'),
             'recordPrestigeVehicleName': event.getArgument('recordPrestigeVehicleName')}
            return PrestigeIndicatorTooltip(params=params)
        else:
            return

    def _getEvents(self):
        vm = self.viewModel
        comp7Ctrl = self.__comp7Controller
        return ((vm.qualificationModel.onRankRewardsPageOpen, self.__onRankRewardsPageOpen),
         (vm.onSelectDay, self.__onSelectDay),
         (vm.onOpenCustomization, self.__onOpenCustomization),
         (vm.onCustomizationProgressShown, self.__onCustomizationProgressShown),
         (vm.onOpenVehicleStats, self.__onOpenVehicleStats),
         (vm.onRefresh, self.__onRefresh),
         (comp7Ctrl.onRankUpdated, self.__updateData),
         (comp7Ctrl.onModeConfigChanged, self.__updateData),
         (comp7Ctrl.onComp7RanksConfigChanged, self.__updateData),
         (comp7Ctrl.onQualificationBattlesUpdated, self.__updateData),
         (comp7Ctrl.onQualificationStateUpdated, self.__updateData),
         (g_playerEvents.onClientUpdated, self.__onClientUpdated),
         (comp7Ctrl.progression.onDataFetched, self.__onProgressionDataUpdate))

    def __updateData(self, *_):
        isQualification = self.__comp7Controller.isQualificationActive()
        if isQualification:
            self.__updateQualificationData()
        else:
            self.__updateProgressionData()

    def __updateQualificationData(self):
        with self.viewModel.transaction() as vm:
            comp7_qualification_helpers.setQualificationInfo(vm.qualificationModel)
            comp7_qualification_helpers.setQualificationBattles(vm.qualificationModel.getBattles())

    def __updateProgressionData(self, *_):
        with self.viewModel.transaction() as vm:
            vm.qualificationModel.setIsActive(False)
            vm.setRankInactivityCount(self.__comp7Controller.activityPoints)
            comp7_model_helpers.setElitePercentage(vm)
            vm.setIsStatisticsLoading(True)
            self.__setCurrentScore(model=vm)
            self.__setRanksItems(model=vm)
        self.__setLeaderBoardAsyncData()
        self.__comp7Controller.progression.requestUpdate()

    def __onClientUpdated(self, diff, _):
        if 'quests' in diff:
            quests = diff['quests']
            if any((qID in quests for qID in self.__custProgQuestIDs)):
                self.__updateCustomizationTasks()

    @replaceNoneKwargsModel
    def __updateSeasonStats(self, model=None):
        if not self.__progressionData:
            return
        else:
            seasonStats = self.__progressionData.getSeasonStats()
            seasonStatsModel = model.seasonStatisticsModel
            aggregatedDailyData = self.__progressionData.aggregatedDailyData
            dayOfMaxRatingIndex = aggregatedDailyData.maxRatingDay
            maxRating = aggregatedDailyData.maxRating
            maxAchievedRank = aggregatedDailyData.maxAchievedRank
            maxDamageVehCD = seasonStats.getMaxDamageVehicle()
            maxDamageVehicle = self.__itemsCache.items.getItemByCD(maxDamageVehCD) if maxDamageVehCD else None
            maxDamageDealt = seasonStats.getMaxDamage()
            maxPrestigeVehCD = seasonStats.getMaxPrestigePointsVehicle()
            maxPrestigeVehicle = self.__itemsCache.items.getItemByCD(maxPrestigeVehCD) if maxPrestigeVehCD else None
            maxPrestige = seasonStats.getMaxPrestigePoints()
            superPlatoonBattlesCount = seasonStats.getSuperSquadBattlesCount() or 0
            soloDuoPlatoonBattlesCount = (seasonStats.getBattlesCount() or 0) - superPlatoonBattlesCount
            winsCount = seasonStats.getWinsCount() or 0
            lossCount = seasonStats.getLossesCount() or 0
            drawCount = seasonStats.getDrawsCount() or 0
            winsEfficiency = seasonStats.getWinsEfficiency()
            avgDmgDealt = seasonStats.getAvgDamage()
            avgPrestige = seasonStats.getAvgPrestigePoints()
            if maxAchievedRank is not None:
                seasonStatsModel.setMaxAchievedRank(maxAchievedRank)
            seasonStatsModel.setMaxAchievedRatingPoints(maxRating)
            seasonStatsModel.setRecordDamageDealt(maxDamageDealt)
            if maxDamageVehicle is not None:
                seasonStatsModel.setRecordDamageDealtVehicleName(maxDamageVehicle.shortUserName)
            seasonStatsModel.setRecordPrestige(maxPrestige)
            if maxPrestigeVehicle is not None:
                seasonStatsModel.setRecordPrestigeVehicleName(maxPrestigeVehicle.shortUserName)
            seasonStatsModel.setDayOfMaxRatingIndex(dayOfMaxRatingIndex)
            seasonStatsModel.setSoloBattlesCount(soloDuoPlatoonBattlesCount)
            seasonStatsModel.setSuperPlatoonBattlesCount(superPlatoonBattlesCount)
            seasonStatsModel.setWinsCount(winsCount)
            seasonStatsModel.setLossCount(lossCount)
            seasonStatsModel.setDrawCount(drawCount)
            if winsEfficiency is not None:
                seasonStatsModel.setWinRate(round(winsEfficiency * 100, 2))
            if avgDmgDealt is not None:
                seasonStatsModel.setAverageDamageDealt(int(round(avgDmgDealt)))
            if avgPrestige is not None:
                seasonStatsModel.setAveragePrestige(int(round(avgPrestige)))
            _logger.debug('__updateSeasonStats %s', str(seasonStatsModel))
            return

    @replaceNoneKwargsModel
    def __updateDailyStats(self, model=None):
        if not self.__progressionData:
            return
        else:
            allDaysData = self.__progressionData.allDaysData
            viewModels = []
            for dayData in allDaysData:
                dayStatsModel = DayStatisticsModel()
                if dayData:
                    maxRating = dayData.maxRatingPoints
                    dayLastRank = dayData.dayPlayerRank
                    maxDamageDealtVehicle = dayData.maxDamageVehicle
                    maxDamageDealt = dayData.maxDamage
                    maxPrestigeVehicle = dayData.maxPrestigePointsVehicle
                    maxPrestige = dayData.maxPrestigePoints
                    lastRatingPoints = dayData.lastRatingPoints
                    totalBattles = dayData.totalBattles
                    superPlatoonBattlesCount = dayData.totalSuperPlatoonBattles
                    soloDuoPlatoonBattlesCount = totalBattles - superPlatoonBattlesCount
                    winsCount = dayData.totalWinsCount
                    lossCount = dayData.totalLossCount
                    drawCount = dayData.totalDrawCount
                    winsEfficiency = dayData.winsEfficiency
                    avgDmgDealt = dayData.avgDmgDealt
                    avgPrestige = dayData.avgPrestige
                    inactivityPenalty = dayData.inactivityPenalty
                    division = dayData.dayRatingPlayerDivision
                    if dayLastRank is not None:
                        dayStatsModel.setMaxAchievedRank(dayLastRank)
                    dayStatsModel.setMaxAchievedRatingPoints(maxRating)
                    dayStatsModel.setRecordDamageDealt(maxDamageDealt)
                    if maxDamageDealtVehicle is not None:
                        dayStatsModel.setRecordDamageDealtVehicleName(maxDamageDealtVehicle.shortUserName)
                    dayStatsModel.setRecordPrestige(maxPrestige)
                    if maxPrestigeVehicle is not None:
                        dayStatsModel.setRecordPrestigeVehicleName(maxPrestigeVehicle.shortUserName)
                    dayStatsModel.setSoloBattlesCount(soloDuoPlatoonBattlesCount)
                    dayStatsModel.setSuperPlatoonBattlesCount(superPlatoonBattlesCount)
                    dayStatsModel.setWinsCount(winsCount)
                    dayStatsModel.setLossCount(lossCount)
                    dayStatsModel.setDrawCount(drawCount)
                    if winsEfficiency is not None:
                        dayStatsModel.setWinRate(round(winsEfficiency * 100, 2))
                    if avgDmgDealt is not None:
                        dayStatsModel.setAverageDamageDealt(int(round(avgDmgDealt)))
                    if avgPrestige is not None:
                        dayStatsModel.setAveragePrestige(int(round(avgPrestige)))
                    dayStatsModel.setIsQualification(dayData.isQualification)
                    dayStatsModel.setDiff(dayData.diffRatingPoints)
                    dayStatsModel.setHasBattles(totalBattles > 0)
                    dayStatsModel.setRatingPoints(lastRatingPoints)
                    dayStatsModel.setRankInactivityPenalty(inactivityPenalty)
                    if division:
                        dayStatsModel.setDivision(Division(division.index))
                    _logger.debug('__updateDailyStats day %s ; %s', str(dayData.dayIndex), str(dayStatsModel))
                viewModels.append(dayStatsModel)

            fillViewModelsArray(viewModels, model.getStatisticsByDay())
            return

    @replaceNoneKwargsModel
    def __updateSeasonVehicleStats(self, model=None):
        if not self.__progressionData:
            return
        else:
            top3SeasonVehicles = self.__progressionData.getTop3SeasonVehicles()
            viewModels = []
            for vehicle in top3SeasonVehicles:
                vehStats = self.__progressionData.getVehicleSeasonStats(vehicle.intCD)
                battlesCount = vehStats.getBattlesCount()
                winsEfficiency = vehStats.getWinsEfficiency()
                avgDamage = vehStats.getAvgDamage()
                avgDamageAssisted = vehStats.getDamageAssistedEfficiencyWithStan()
                avgPrestigePoints = vehStats.getAvgPrestigePoints()
                damageEfficiency = vehStats.getDamageEfficiency()
                fragsEfficiency = vehStats.getFragsEfficiency()
                vehicleStatModel = TopVehicleStatisticsModel()
                if battlesCount is not None:
                    vehicleStatModel.setBattles(battlesCount)
                if winsEfficiency is not None:
                    vehicleStatModel.setWinSeries(round(winsEfficiency * 100, 2))
                if avgDamage is not None:
                    vehicleStatModel.setDamage(int(round(avgDamage)))
                if avgDamageAssisted is not None:
                    vehicleStatModel.setAssist(int(round(avgDamageAssisted)))
                if avgPrestigePoints is not None:
                    vehicleStatModel.setPrestigePoints(int(round(avgPrestigePoints)))
                if damageEfficiency is not None:
                    vehicleStatModel.setMaxFrags(round(damageEfficiency, 2))
                if fragsEfficiency is not None:
                    vehicleStatModel.setDestruction(round(fragsEfficiency, 2))
                fillVehicleModel(vehicleStatModel, vehicle)
                _logger.debug('__updateSeasonVehicleStats vehicle %s ; %s', str(vehicle.shortUserName), str(vehicleStatModel))
                viewModels.append(vehicleStatModel)

            fillViewModelsArray(viewModels, model.getTopVehiclesStatistics())
            return

    @replaceNoneKwargsModel
    def __updateDailyVehicleStats(self, dayIndex, model=None):
        if not self.__progressionData:
            return
        else:
            dayData = self.__progressionData.allDaysData[dayIndex]
            viewModels = []
            if not dayData:
                return
            for vehicleCD in dayData.topVehiclesCDs:
                vehicleData = dayData.dataPerVehicle.get(vehicleCD)
                vehicle = self.__itemsCache.items.getItemByCD(vehicleData.vehicleCD)
                battlesCount = vehicleData.totalBattles
                winsEfficiency = vehicleData.winsEfficiency
                avgDamage = vehicleData.avgDamage
                avgDamageAssisted = vehicleData.avgDamageAssisted
                avgPrestigePoints = vehicleData.avgPrestigePoints
                damageEfficiency = vehicleData.damageEfficiency
                fragsEfficiency = vehicleData.fragsEfficiency
                vehicleStatModel = TopVehicleStatisticsModel()
                if battlesCount is not None:
                    vehicleStatModel.setBattles(battlesCount)
                if winsEfficiency is not None:
                    vehicleStatModel.setWinSeries(round(winsEfficiency * 100, 2))
                if avgDamage is not None:
                    vehicleStatModel.setDamage(int(round(avgDamage)))
                if avgDamageAssisted is not None:
                    vehicleStatModel.setAssist(int(round(avgDamageAssisted)))
                if avgPrestigePoints is not None:
                    vehicleStatModel.setPrestigePoints(int(round(avgPrestigePoints)))
                if damageEfficiency is not None:
                    vehicleStatModel.setMaxFrags(round(damageEfficiency, 2))
                if fragsEfficiency is not None:
                    vehicleStatModel.setDestruction(round(fragsEfficiency, 2))
                fillVehicleModel(vehicleStatModel, vehicle)
                _logger.debug('__updateDailyVehicleStats day %s %s %s', str(dayData.dayIndex), str(vehicle.shortUserName), str(vehicleStatModel))
                viewModels.append(vehicleStatModel)

            fillViewModelsArray(viewModels, model.getTopVehiclesStatistics())
            return

    @replaceNoneKwargsModel
    def __setCurrentScore(self, model=None):
        currentScore = self.__comp7Controller.rating
        model.setCurrentScore(currentScore)

    @replaceNoneKwargsModel
    def __setRanksItems(self, model=None):
        itemsArray = model.getItems()
        itemsArray.clear()
        for rank in self.ranksConfig.ranksOrder:
            itemModel = ProgressionItemModel()
            itemModel.setHasRankInactivity(comp7_shared.hasRankInactivity(rank))
            meta_view_helper.setProgressionItemData(itemModel, model, rank, self.ranksConfig)
            itemsArray.addViewModel(itemModel)

        itemsArray.invalidate()

    @adisp_process
    def __setLeaderBoardAsyncData(self):
        self.viewModel.setIsLastBestUserPointsValueLoading(True)
        lbUpdateTime, isSuccess = yield self.__comp7Controller.leaderboard.getLastUpdateTime()
        if not self.isLoaded:
            return
        if isSuccess:
            self.__lastUpdateTime = lbUpdateTime
            self.viewModel.setLeaderboardUpdateTimestamp(lbUpdateTime or 0)
        lastRatingValue, isSuccess = yield self.__comp7Controller.leaderboard.getLastEliteRating()
        if not self.isLoaded:
            return
        if isSuccess:
            self.viewModel.setLastBestUserPointsValue(lastRatingValue or 0)
        self.viewModel.setIsLastBestUserPointsValueLoading(not isSuccess)

    def __onProgressionDataUpdate(self):
        self.__progressionData = self.__comp7Controller.progression.playerProgression
        with self.viewModel.transaction() as vm:
            vm.setIsStatisticsLoading(False)
            if self.__progressionData:
                vm.setStatisticsUpdateTimestamp(self.__comp7Controller.progression.lastUpdatedTimestamp)
            else:
                vm.setPageState(PageState.ERROR)
                return
            allDaysData = self.__progressionData.allDaysData
            todayIndex = self.__progressionData.todayIndex
            todayData = allDaysData[todayIndex] if len(allDaysData) > todayIndex else None
            isBattlesPlayedToday = todayData and todayData.totalBattles > 0 if allDaysData else False
            selectedDayIndex = self.__selectedDayIndex or (todayIndex if isBattlesPlayedToday else None)
            vm.setCurrentDayIndex(todayIndex)
            if selectedDayIndex is not None:
                -1 < selectedDayIndex < len(allDaysData) and self.__updateDailyVehicleStats(selectedDayIndex, model=vm)
                vm.setStatisticsMode(StatisticsMode.DAY)
                vm.setSelectedDayIndex(selectedDayIndex)
                self.__selectedDayIndex = selectedDayIndex
            else:
                self.__updateSeasonVehicleStats(model=vm)
                vm.setStatisticsMode(StatisticsMode.SEASON)
            self.__updateDailyStats(model=vm)
            self.__updateSeasonStats(model=vm)
            vm.setPageState(PageState.SUCCESS)
        return

    def __onRankRewardsPageOpen(self):
        showComp7MetaRootTab(MetaRootViews.RANKREWARDS)

    @args2params(int)
    def __onSelectDay(self, index):
        with self.viewModel.transaction() as vm:
            vm.setSelectedDayIndex(index)
            if index == -1:
                self.__updateSeasonVehicleStats(model=vm)
                vm.setStatisticsMode(StatisticsMode.SEASON)
            else:
                self.__updateDailyVehicleStats(index, model=vm)
                vm.setStatisticsMode(StatisticsMode.DAY)
            self.__selectedDayIndex = index

    def __onOpenVehicleStats(self):
        showComp7SeasonVehiclesStatisticsView()

    def __onRefresh(self):
        self.__updateData()

    def __updateCustomizationTasks(self):
        if self.__comp7Controller.isQualificationActive():
            return
        else:
            style = getComp7ProgressionStyle()
            if style is None:
                _logger.error('Style could not be found')
                return
            allTokens = self.__itemsCache.items.tokens.getTokens()
            cacher = self.__c11nProgressCacher
            self.__custProgQuestIDs = questIDs = []
            itemsData = []
            for item in style.alternateItems:
                quests = item.getUnlockingQuests()
                if not quests or not isC11nItemTokenAttainable(allTokens, item):
                    continue
                quest = first(quests)
                iconKey = item.texture.split('/')[-1].split('.')[0]
                description, currentProgress, maxProgress = getDescriptionAndProgressFromC11nDecalQuest(quest)
                delta = cacher.getDelta(item.intCD, currentProgress)
                level = item.descriptor.requiredTokenCount if item.itemTypeID == GUI_ITEM_TYPE.EMBLEM else 0
                questIDs.append(quest.getID())
                itemsData.append((description,
                 currentProgress,
                 maxProgress,
                 iconKey,
                 item.intCD,
                 delta,
                 level))

            itemsData.sort(key=_c11nTaskSortKey, reverse=True)
            self.__populateCustomizationTasksModels(itemsData)
            cacher.reset(questIDs)
            cacher.setUiFlag()
            return

    def __populateCustomizationTasksModels(self, itemsData):
        with self.getViewModel().transaction() as tx:
            models = tx.getCustomizationTasks()
            models.clear()
            addViewModel = models.addViewModel
            for description, currentProgress, maxProgress, iconKey, intCD, delta, level in itemsData:
                model = CustomizationTasksModel()
                model.setDescription(description)
                model.setCurrentProgress(currentProgress)
                model.setMaxProgress(maxProgress)
                model.setIconKey(iconKey)
                model.setCustomizationId(intCD)
                model.setDelta(delta)
                if level:
                    model.setProgressionLevel(level)
                addViewModel(model)

            models.invalidate()

    def __onCustomizationProgressShown(self, args):
        decalCD = int(args.get('customizationId', 0))
        with self.getViewModel().transaction() as tx:
            for task in tx.getCustomizationTasks():
                if task.getCustomizationId() == decalCD:
                    task.setDelta(0)
                    progress = task.getCurrentProgress()
                    self.__c11nProgressCacher.setProgress(decalCD, progress)
                    self.__c11nProgressCacher.setUiFlag()
                    break
            else:
                _logger.error('Customization task not found decalCD = %s', decalCD)

    def __onOpenCustomization(self, args):
        decalCD = int(args.get('customizationId', 0))
        style = getComp7ProgressionStyle()
        if style is None:
            _logger.error('Style could not be found')
            return
        else:
            items = self.__itemsCache.items
            vehicle, error = getVehicleForStyle(items, REQ_CRITERIA.CUSTOM(style.isInstallableOnVehicle), getMaxLevelAndBattlesVehicleSortKey(items), style, g_currentVehicle.item if g_currentVehicle else None)
            if error:
                resource = R.strings.comp7_ext.progressionPage.error
                if error == 'noValidVehicles':
                    pushMessage(text(resource.noVehiclesForStyle()), SM_TYPE.ErrorSimple, Priority.MEDIUM)
                elif error == 'allStylesInstalledOnInvalids':
                    pushMessage(text(resource.noStylesForVehicle()), SM_TYPE.ErrorSimple, Priority.MEDIUM)
                else:
                    _logger.error('Vehicle could not be found with undefined error, reason = %s', error)
                return
            self.__c11n.showCustomization(vehInvID=vehicle.invID, modeId=CustomizationModes.STYLE_2D, itemCD=style.intCD, tabId=CustomizationTabs.STYLES_2D, callback=partial(selectStyleAndDecalInC11nHangar, self.__c11n, items, style.intCD, decalCD))
            return


def _c11nTaskSortKey(data):
    currentProgress = data[1]
    maxProgress = data[2]
    return float(currentProgress) / float(maxProgress) if maxProgress > 0.0 else 0.0
