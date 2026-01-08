# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/event_boards/event_boards_items.py
import datetime
import typing
import math
from comp7.gui.shared.gui_items.dossier.stats import getComp7DossierStats
from comp7.gui.impl.lobby.comp7_helpers.comp7_shared import getRankEnumValue, getPlayerDivisionByDvsnID
from gui.event_boards.event_boards_items import LeaderBoard, IPlayerProgression, isDataSchemaValid
from helpers import time_utils
from helpers.dependency import descriptor
from helpers_common import reprSlots
from shared_utils import first
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from comp7.gui.impl.gen.view_models.views.lobby.enums import Rank
    from comp7_ranks_common import Comp7Division
    from comp7_ranks_common import Comp7RanksConfig
    from comp7.gui.shared.gui_items.dossier.stats import AccountComp7StatsBlock
    from comp7.gui.shared.gui_items.dossier.stats import Comp7StatsBlock
    from typing import Tuple
    from typing import List, Optional
    from gui.shared.gui_items.Vehicle import Vehicle

class BattleUnitTypeData(object):
    __slots__ = ('solo', 'platoon', 'superPlatoon', 'total')

    def __init__(self, rawBattleUnitData):
        self.solo = rawBattleUnitData[0]
        self.platoon = rawBattleUnitData[1]
        self.superPlatoon = rawBattleUnitData[2]
        self.total = self.solo + self.platoon + self.superPlatoon


class DailyVehicleData(object):
    __slots__ = ('dayIndex', 'vehicleCD', 'prestigePoints', 'totalDeathsPerUnitType', 'totalAssistedPerUnitType', 'damageReceivedPerUnitType', 'battleCountWinPerUnitType', 'battleCountLossPerUnitType', 'battleCountDrawPerUnitType', 'totalDamagePerUnitType', 'firstBattleTimestampsPerUnitType', 'fragsPerUnitType', 'lastBattleTimestampsPerUnitType', 'battleLengthTotalSecondsPerUnitType', 'totalSuperPlatoonBattles', 'totalPlatoonBattles', 'totalSoloBattles', 'totalBattles', 'damageEfficiency', 'fragsEfficiency', 'winsEfficiency', 'avgDamage', 'avgDamageAssisted', 'avgPrestigePoints')

    def __init__(self, vehicleCD, rawDailyVehicleData, dayIndex):
        self.dayIndex = dayIndex
        self.vehicleCD = vehicleCD
        self.prestigePoints = rawDailyVehicleData['prestige_points']
        self.totalDeathsPerUnitType = BattleUnitTypeData(rawDailyVehicleData['total_deaths'])
        self.totalAssistedPerUnitType = BattleUnitTypeData(rawDailyVehicleData['total_assisted'])
        self.damageReceivedPerUnitType = BattleUnitTypeData(rawDailyVehicleData['total_received_damage'])
        self.battleCountWinPerUnitType = BattleUnitTypeData(rawDailyVehicleData['battle_count_win'])
        self.battleCountLossPerUnitType = BattleUnitTypeData(rawDailyVehicleData['battle_count_loss'])
        self.battleCountDrawPerUnitType = BattleUnitTypeData(rawDailyVehicleData['battle_count_draw'])
        self.totalDamagePerUnitType = BattleUnitTypeData(rawDailyVehicleData['total_damage'])
        self.firstBattleTimestampsPerUnitType = BattleUnitTypeData(rawDailyVehicleData['first_battle'])
        self.fragsPerUnitType = BattleUnitTypeData(rawDailyVehicleData['battle_count_win'])
        self.lastBattleTimestampsPerUnitType = BattleUnitTypeData(rawDailyVehicleData['last_battle'])
        self.battleLengthTotalSecondsPerUnitType = BattleUnitTypeData(rawDailyVehicleData['battle_length_total_seconds'])
        losses, wins, draws = self.battleCountLossPerUnitType, self.battleCountWinPerUnitType, self.battleCountDrawPerUnitType
        self.totalSuperPlatoonBattles = losses.superPlatoon + wins.superPlatoon + draws.superPlatoon
        self.totalPlatoonBattles = losses.platoon + wins.platoon + draws.platoon
        self.totalSoloBattles = losses.solo + wins.solo + draws.solo
        self.totalBattles = losses.total + wins.total + draws.total
        self.damageEfficiency = None
        damageReceivedTotal = self.damageReceivedPerUnitType.total
        if damageReceivedTotal > 0:
            self.damageEfficiency = float(self.totalDamagePerUnitType.total) / damageReceivedTotal
        self.fragsEfficiency = None
        destroyedTotal = self.totalDeathsPerUnitType.total
        if destroyedTotal > 0:
            self.fragsEfficiency = float(self.fragsPerUnitType.total) / destroyedTotal
        self.winsEfficiency = None
        self.avgDamage = None
        self.avgDamageAssisted = None
        self.avgPrestigePoints = None
        if self.totalBattles > 0:
            self.winsEfficiency = float(self.battleCountWinPerUnitType.total) / self.totalBattles
            self.avgDamage = float(self.totalDamagePerUnitType.total) / self.totalBattles
            self.avgDamageAssisted = float(self.totalAssistedPerUnitType.total) / self.totalBattles
            self.avgPrestigePoints = math.ceil(float(self.prestigePoints) / self.totalBattles)
        return


class DailyData(object):
    _itemsCache = descriptor(IItemsCache)
    __slots__ = ('dayIndex', 'lastRatingPoints', 'lastDivision', 'maxDamage', 'inactivityPenalty', 'maxRatingPoints', 'lastActivityPoints', 'maxPrestigePoints', 'dataPerVehicle', 'date', 'maxDamageVehicle', 'maxPrestigePointsVehicle', 'isQualification', 'diffRatingPoints', 'totalDamage', 'maxDivisionIndex', 'totalPrestigePoints', 'totalSuperPlatoonBattles', 'totalPlatoonBattles', 'totalSoloBattles', 'totalBattles', 'totalWinsCount', 'totalLossCount', 'totalDrawCount', 'dayRatingPlayerDivision', 'dayPlayerRank', 'maxPlayerRank', 'winsEfficiency', 'avgDmgDealt', 'avgPrestige', 'topVehiclesCDs')

    def __init__(self, dayIndex, rawDailyData, qualificationCompleteDate, previousDayRatingPoints):
        self.dayIndex = dayIndex
        self.lastRatingPoints = rawDailyData.get('last_rating_points', 0)
        self.lastDivision = rawDailyData.get('last_division', 0)
        self.maxDamage = rawDailyData.get('max_damage', 0)
        maxDamageVehCD = rawDailyData.get('max_damage_veh_cd', '')
        self.inactivityPenalty = rawDailyData.get('inactivity_penalty', 0)
        self.maxDivisionIndex = rawDailyData.get('max_rating_points_division', 0)
        self.maxRatingPoints = rawDailyData.get('max_rating_points', 0)
        self.lastActivityPoints = rawDailyData.get('last_activity_points', 0)
        self.maxPrestigePoints = rawDailyData.get('max_prestige_points', 0)
        maxPrestigePointsVehCD = rawDailyData.get('max_prestige_points_veh_cd', '')
        self.dataPerVehicle = {}
        for vehicleCD, rawDailyVehicleData in rawDailyData.get('vehicles', {}).items():
            self.dataPerVehicle[int(vehicleCD)] = DailyVehicleData(int(vehicleCD), rawDailyVehicleData, dayIndex)

        self.date = _dateStrToDatetime(rawDailyData.get('date'))
        self.maxDamageVehicle = None
        if maxDamageVehCD:
            self.maxDamageVehicle = self._itemsCache.items.getItemByCD(int(maxDamageVehCD))
        self.maxPrestigePointsVehicle = None
        if maxPrestigePointsVehCD:
            self.maxPrestigePointsVehicle = self._itemsCache.items.getItemByCD(int(maxPrestigePointsVehCD))
        isQualificationCompleted = self.date and qualificationCompleteDate and qualificationCompleteDate <= self.date
        self.isQualification = not isQualificationCompleted
        self.diffRatingPoints = self.lastRatingPoints - previousDayRatingPoints
        self.totalDamage = 0
        self.totalPrestigePoints = 0
        self.totalSuperPlatoonBattles = 0
        self.totalPlatoonBattles = 0
        self.totalSoloBattles = 0
        self.totalBattles = 0
        self.totalWinsCount = 0
        self.totalLossCount = 0
        self.totalDrawCount = 0
        for v in self.dataPerVehicle.values():
            self.totalDamage += v.totalDamagePerUnitType.total
            self.totalPrestigePoints += v.prestigePoints
            self.totalSuperPlatoonBattles += v.totalSuperPlatoonBattles
            self.totalPlatoonBattles += v.totalPlatoonBattles
            self.totalSoloBattles += v.totalSoloBattles
            self.totalBattles += v.totalBattles
            self.totalWinsCount += v.battleCountWinPerUnitType.total
            self.totalLossCount += v.battleCountLossPerUnitType.total
            self.totalDrawCount += v.battleCountDrawPerUnitType.total

        self.dayRatingPlayerDivision = None
        self.dayPlayerRank = None
        if self.lastDivision:
            self.dayRatingPlayerDivision = getPlayerDivisionByDvsnID(self.lastDivision)
            if self.dayRatingPlayerDivision:
                self.dayPlayerRank = getRankEnumValue(self.dayRatingPlayerDivision)
        self.maxPlayerRank = None
        if self.maxRatingPoints > 0:
            maxRankDivision = getPlayerDivisionByDvsnID(self.maxDivisionIndex)
            if maxRankDivision:
                self.maxPlayerRank = getRankEnumValue(maxRankDivision)
        self.winsEfficiency = None
        self.avgDmgDealt = None
        self.avgPrestige = None
        if self.totalBattles > 0:
            self.winsEfficiency = float(self.totalWinsCount) / self.totalBattles
            self.avgDmgDealt = float(self.totalDamage) / self.totalBattles
            self.avgPrestige = math.ceil(float(self.totalPrestigePoints) / self.totalBattles)
        self.topVehiclesCDs = self.__getSortedTopDailyVehiclesCDs()[:3]
        return

    def __getSortedTopDailyVehiclesCDs(self):
        sortKey = lambda vehicleDayData: (-vehicleDayData.totalBattles, self._itemsCache.items.getItemByCD(vehicleDayData.vehicleCD).nationName, vehicleDayData.vehicleCD)
        sortedDayVehiclesData = sorted(self.dataPerVehicle.values(), key=sortKey)
        return [ dayVehicleData.vehicleCD for dayVehicleData in sortedDayVehiclesData ]

    __repr__ = reprSlots


class AggregatedDailyData(object):
    _comp7Ctrl = descriptor(IComp7Controller)
    __slots__ = ('__allDaysData', 'maxRatingDay', 'maxRating', 'maxAchievedRank')

    def __init__(self, allDaysData):
        self.__allDaysData = allDaysData
        self.maxRatingDay, self.maxRating = self.__getMaxDayAndRating()
        self.maxAchievedRank = self.__getMaxAchievedRank()

    def __getMaxAchievedRank(self):
        maxRank = None
        for dayData in self.__allDaysData:
            if dayData and dayData.maxPlayerRank and (not maxRank or maxRank.value > dayData.maxPlayerRank.value):
                maxRank = dayData.maxPlayerRank

        return maxRank

    def __getMaxDayAndRating(self):
        dayOfMaxRating, maxRating = (0, 0)
        for dayData in self.__allDaysData:
            if dayData and dayData.maxRatingPoints > maxRating:
                dayOfMaxRating, maxRating = dayData.dayIndex, dayData.maxRatingPoints

        return (dayOfMaxRating, maxRating)


class Comp7LeaderBoard(LeaderBoard):
    __CUSTOM_EXPECTED_FIELDS_META = ['elite_rank_position_threshold', 'elite_rank_points_threshold', 'master_rank_position_threshold']
    EXPECTED_FIELDS_META = LeaderBoard.EXPECTED_FIELDS_META + __CUSTOM_EXPECTED_FIELDS_META

    def __init__(self):
        super(Comp7LeaderBoard, self).__init__()
        self.__lastEliteUserPosition = None
        self.__lastEliteUserRating = None
        self.__lastMasterRankPositionThreshold = None
        return

    def setData(self, rawData, leaderboardID, infoType, leaderboardType):
        result = super(Comp7LeaderBoard, self).setData(rawData, leaderboardID, infoType, leaderboardType)
        meta = rawData['meta']
        self.__lastEliteUserPosition = meta['elite_rank_position_threshold']
        self.__lastEliteUserRating = meta['elite_rank_points_threshold']
        self.__lastMasterRankPositionThreshold = meta['master_rank_position_threshold'] or 0
        return result

    def getRecordsCount(self):
        return self.__lastMasterRankPositionThreshold

    def getLastEliteUserPosition(self):
        return self.__lastEliteUserPosition

    def getLastEliteUserRating(self):
        return self.__lastEliteUserRating


class Comp7PlayerProgression(IPlayerProgression):
    _comp7Ctrl = descriptor(IComp7Controller)
    _itemsCache = descriptor(IItemsCache)
    _DAYS_FIELD = 'days'
    _META_FIELD = 'meta'
    _EXPECTED_ROOT_FIELDS = (_DAYS_FIELD, _META_FIELD)
    _EXPECTED_DAY_FIELDS = ('date', 'vehicles', 'max_rating_points_division', 'max_rating_points', 'last_rating_points', 'last_division', 'last_activity_points', 'inactivity_penalty', 'max_prestige_points', 'max_prestige_points_veh_cd', 'max_damage', 'max_damage_veh_cd')
    _EXPECTED_META_FIELDS = ('last_update', 'qualification_complete_date')
    _EXPECTED_VEHICLE_FIELDS = ('frags', 'last_battle', 'first_battle', 'total_damage', 'total_assisted', 'prestige_points', 'battle_count_win', 'battle_count_draw', 'battle_count_loss', 'battle_length_total_seconds', 'total_received_damage', 'total_deaths')

    def __init__(self, rawData, eventID, leaderboardID):
        super(Comp7PlayerProgression, self).__init__(rawData, eventID, leaderboardID)
        self.eventID = eventID
        self.__meta = meta = rawData[self._META_FIELD]
        self.__lastUpdate = meta.get('last_update', datetime.datetime.min)
        self.season = self._comp7Ctrl.getCurrentSeason() or self._comp7Ctrl.getPreviousSeason()
        seasonStartTs = self.season.getStartDate()
        seasonEndTs = self.season.getEndDate()
        seasonStartDt = time_utils.getDateTimeInUTC(seasonStartTs)
        ranksConfig = self._comp7Ctrl.getRanksConfig()
        todayBusinessDate = self.__getBusinessDate(datetime.datetime.utcnow(), ranksConfig)
        rawDayDataByDate = {_dateStrToDatetime(dayRawData['date']).date():dayRawData for dayRawData in rawData['days']}
        seasonStartBusinessDate = self.__getBusinessDate(seasonStartDt, ranksConfig)
        if self.__isPrimeHourBefore(seasonStartDt.hour):
            seasonStartBusinessDate += datetime.timedelta(days=1)
        seasonEndBusinessDate = self.__getBusinessDate(time_utils.getDateTimeInUTC(seasonEndTs), ranksConfig)
        daysInSeasonCount = (seasonEndBusinessDate - seasonStartBusinessDate).days + 1
        qualDate = _dateStrToDatetime(meta.get('qualification_complete_date'))
        lastKnownDayData = None
        self.__allDaysData = []
        for i in range(daysInSeasonCount):
            seasonDayDateTime = seasonStartBusinessDate + datetime.timedelta(days=i)
            rawDayData = rawDayDataByDate.get(seasonDayDateTime, {})
            if not rawDayData:
                rawDayData = {'date': seasonDayDateTime.strftime('%Y-%m-%d'),
                 'last_rating_points': lastKnownDayData.lastRatingPoints if lastKnownDayData else 0,
                 'last_division': lastKnownDayData.lastDivision if lastKnownDayData else 0,
                 'max_rating_points_division': lastKnownDayData.maxDivisionIndex if lastKnownDayData else 0,
                 'max_rating_points': lastKnownDayData.maxRatingPoints if lastKnownDayData else 0}
            previousDayRatingPoints = lastKnownDayData.lastRatingPoints if lastKnownDayData else 0
            dailyData = DailyData(i, rawDayData, qualDate, previousDayRatingPoints)
            self.__allDaysData.append(dailyData)
            if rawDayData:
                lastKnownDayData = dailyData

        self.__aggregatedDailyData = AggregatedDailyData(self.__allDaysData)
        self.__todayIndex = (todayBusinessDate - seasonStartBusinessDate).days
        return

    @property
    def todayIndex(self):
        return self.__todayIndex

    @property
    def lastUpdateTime(self):
        return time_utils.getTimestampFromISO(self.__lastUpdate)

    @property
    def allDaysData(self):
        return self.__allDaysData

    @property
    def aggregatedDailyData(self):
        return self.__aggregatedDailyData

    def getVehicleSeasonStats(self, vehCD, seasonNumber=None):
        if seasonNumber is None:
            seasonNumber = self.season.getNumber()
        vehDossier = self._itemsCache.items.getVehicleDossier(vehCD)
        return getComp7DossierStats(vehDossier, season=seasonNumber)

    def getSeasonStats(self, seasonNumber=None):
        if seasonNumber is None:
            seasonNumber = self.season.getNumber()
        accDossier = self._itemsCache.items.getAccountDossier()
        return getComp7DossierStats(accDossier, season=seasonNumber)

    def getTop3SeasonVehicles(self):
        accDossier = self._itemsCache.items.getAccountDossier()
        seasonNumber = self.season.getNumber()
        seasonStats = getComp7DossierStats(accDossier, season=seasonNumber)
        seasonStatsVehicles = seasonStats.getVehicles()
        if not seasonStatsVehicles:
            return []
        sortKey = lambda vStat: (-vStat[1].battlesCount, self._itemsCache.items.getItemByCD(vStat[0]).nationName, vStat[0])
        sortedVehicles = sorted(seasonStatsVehicles.items(), key=sortKey)
        return [ self._itemsCache.items.getItemByCD(vehicleCD) for vehicleCD, _ in sortedVehicles[:3] ]

    @classmethod
    def _isDataStructureValid(cls, data):
        return bool(data) and isDataSchemaValid(cls._EXPECTED_ROOT_FIELDS, data) and isDataSchemaValid(cls._EXPECTED_META_FIELDS, data[cls._META_FIELD]) and all((isDataSchemaValid(cls._EXPECTED_DAY_FIELDS, day) for day in data[cls._DAYS_FIELD])) and all((isDataSchemaValid(cls._EXPECTED_VEHICLE_FIELDS, vehicleData) for day in data[cls._DAYS_FIELD] for vehicleData in day['vehicles'].itervalues()))

    def __getBusinessDate(self, dt, ranksConfig):
        isDtInPreviousBusinessDay = dt.hour < ranksConfig.businessDayStartHour
        seasonEndBusinessDt = dt - datetime.timedelta(days=1) if isDtInPreviousBusinessDay else dt
        return seasonEndBusinessDt.date()

    def __isPrimeHourBefore(self, hour):
        comp7ModeSettings = self._comp7Ctrl.getModeSettings()
        firstPrimeTimeStartHour = first(first(comp7ModeSettings.primeTimes.values(), {}).get('start'))
        return True if firstPrimeTimeStartHour and firstPrimeTimeStartHour < hour else False


def _dateStrToDatetime(dateStr):
    return datetime.datetime.strptime(dateStr, '%Y-%m-%d') if dateStr else None
