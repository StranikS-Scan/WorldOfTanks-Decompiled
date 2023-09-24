# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/season_statistics.py
import typing
import BigWorld
import SoundGroups
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from comp7_common import seasonPointsCodeBySeasonNumber
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from frameworks.wulf.view.array import fillViewModelsArray, fillStringsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.season_statistics_model import SeasonStatisticsModel, SeasonPointState, SummaryStatisticsModel, VehicleStatisticsModel, SeasonName
from gui.impl.gen.view_models.views.lobby.comp7.constants import Constants
from gui.impl.gen.view_models.views.lobby.comp7.summary_statistics_model import SummaryStatisticsType
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.comp7 import comp7_shared
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.dossier.stats import AccountComp7StatsBlock
SOUND_NAME = 'comp_7_season_statistics_screen_appear'

class SeasonStatistics(ViewImpl):
    __slots__ = ('__summaryStatistics', '__seasonNumber')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)
    __webCtrl = dependency.descriptor(IWebController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, layoutID, seasonNumber):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = SeasonStatisticsModel()
        super(SeasonStatistics, self).__init__(settings)
        self.__seasonNumber = seasonNumber
        self.__summaryStatistics = [BattlesStat,
         DamageStat,
         PrestigePointsStat,
         FragsStat,
         WinSeriesStat]

    @property
    def viewModel(self):
        return super(SeasonStatistics, self).getViewModel()

    def _onLoading(self, *_, **__):
        self.__setComp7SeasonStasisticsShown()
        self.__addListeners()
        self.__updateData()
        self.__playSound()

    def _finalize(self):
        self.__removeListeners()

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose

    def __setComp7SeasonStasisticsShown(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.COMP7_SEASON_STATISTICS_SHOWN] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

    def __updateData(self):
        with self.viewModel.transaction() as tx:
            self.__updatePersonalData(tx)
            self.__updateSeasonPoints(tx)
            self.__updateSummaryStatistics(tx)
            self.__updateVehicleStats(tx)

    def __updatePersonalData(self, model):
        model.setUserName(BigWorld.player().name)
        model.setScore(self.__comp7Controller.rating)
        clanProfile = self.__webCtrl.getAccountProfile()
        if clanProfile.isInClan():
            model.setClanTag(clanProfile.getClanAbbrev())
            model.setClanTagColor('#FFFFFF')
        division = comp7_shared.getPlayerDivision()
        model.setDivision(comp7_shared.getDivisionEnumValue(division))
        model.setRank(comp7_shared.getRankEnumValue(division))
        model.setSeason(list(SeasonName)[self.__seasonNumber - 1])

    def __updateSeasonPoints(self, model):
        seasonPointsCode = seasonPointsCodeBySeasonNumber(self.__seasonNumber)
        receivedSeasonPoints = self.__comp7Controller.getReceivedSeasonPoints().get(seasonPointsCode, 0)
        maxSeasonPoints = self.__comp7Controller.getMaxAvailableSeasonPoints()
        result = [SeasonPointState.ACHIEVED.value] * receivedSeasonPoints
        if len(result) < maxSeasonPoints:
            result += [SeasonPointState.NOTACHIEVED.value] * (maxSeasonPoints - receivedSeasonPoints)
        fillStringsArray(result, model.getSeasonPoints())

    def __updateSummaryStatistics(self, model):
        accDossier = self.__itemsCache.items.getAccountDossier()
        seasonStats = accDossier.getComp7Stats(season=self.__seasonNumber)
        viewModels = []
        for stat in self.__summaryStatistics:
            statInstance = stat(seasonStats)
            statistic = SummaryStatisticsModel()
            statistic.setType(statInstance.statType)
            statistic.setMain(statInstance.mainStat())
            statistic.setAdditional(statInstance.additionalStat() or 0)
            viewModels.append(statistic)

        fillViewModelsArray(viewModels, model.getSummaryStatistics())

    def __updateVehicleStats(self, model):
        accDossier = self.__itemsCache.items.getAccountDossier()
        vehicles = accDossier.getComp7Stats(season=self.__seasonNumber).getVehicles()
        if not vehicles:
            return
        viewModels = []
        sortedVehicles = sorted(vehicles.items(), key=lambda vStat: vStat[1].battlesCount, reverse=True)
        for vehicleCD, vehicleStats in sortedVehicles[:3]:
            vehicle = self.__itemsCache.items.getVehicleCopyByCD(vehicleCD)
            statistic = VehicleStatisticsModel()
            statistic.setBattles(vehicleStats.battlesCount)
            statistic.setWinsPercent(vehicleStats.wins * 100 / vehicleStats.battlesCount)
            fillVehicleModel(statistic.vehicleInfo, vehicle)
            viewModels.append(statistic)

        fillViewModelsArray(viewModels, model.getVehicleStatistics())

    @staticmethod
    def __playSound():
        SoundGroups.g_instance.playSound2D(SOUND_NAME)

    def __onClose(self):
        self.destroyWindow()


class SummarySeasonStat(object):

    def __init__(self, seasonStats):
        self._seasonStats = seasonStats

    @property
    def statType(self):
        raise NotImplementedError

    def mainStat(self):
        raise NotImplementedError

    def additionalStat(self):
        raise NotImplementedError


class BattlesStat(SummarySeasonStat):

    @property
    def statType(self):
        return SummaryStatisticsType.BATTLES

    def mainStat(self):
        return self._seasonStats.getBattlesCount()

    def additionalStat(self):
        battlesCount = self._seasonStats.getBattlesCount()
        return self._seasonStats.getWinsCount() * 100 / battlesCount


class DamageStat(SummarySeasonStat):

    @property
    def statType(self):
        return SummaryStatisticsType.DAMAGE

    def mainStat(self):
        return self._seasonStats.getMaxDamage()

    def additionalStat(self):
        return self._seasonStats.getAvgDamage()


class PrestigePointsStat(SummarySeasonStat):

    @property
    def statType(self):
        return SummaryStatisticsType.MAXPRESTIGEPOINTS

    def mainStat(self):
        return self._seasonStats.getMaxPrestigePoints()

    def additionalStat(self):
        return self._seasonStats.getAvgPrestigePoints()


class FragsStat(SummarySeasonStat):

    @property
    def statType(self):
        return SummaryStatisticsType.MAXFRAGS

    def mainStat(self):
        return self._seasonStats.getMaxFrags()

    def additionalStat(self):
        efficiency = self._seasonStats.getFragsEfficiency()
        return Constants.NOT_AVAILABLE_STATISTIC_VALUE if efficiency is None else efficiency


class WinSeriesStat(SummarySeasonStat):

    @property
    def statType(self):
        return SummaryStatisticsType.WINSERIES

    def mainStat(self):
        return self._seasonStats.getMaxWinSeries()

    def additionalStat(self):
        return self._seasonStats.getMaxSquadWinSeries()


class SeasonStatisticsWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, seasonNumber, parent=None):
        super(SeasonStatisticsWindow, self).__init__(wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW, content=SeasonStatistics(layoutID=R.views.lobby.comp7.SeasonStatistics(), seasonNumber=seasonNumber), parent=parent)
