# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/stats.py
import itertools
import logging
from collections import namedtuple, defaultdict
import constants
import nations
from dossiers2.ui import layouts
from dossiers2.ui.achievements import ACHIEVEMENT_MODE, ACHIEVEMENT_SECTION, ACHIEVEMENT_SECTIONS_INDICES, makeAchievesStorageName, ACHIEVEMENT_SECTIONS_ORDER, getSection as getAchieveSection
from gui.shared.gui_items.dossier.achievements import mark_of_mastery
from gui.shared.gui_items.dossier.factories import getAchievementFactory, _SequenceAchieveFactory
from items import vehicles
from soft_exception import SoftException
_logger = logging.getLogger(__name__)
UNAVAILABLE_MARKS_OF_MASTERY = (-1, -1, -1, -1)
_BATTLE_SECTION = ACHIEVEMENT_SECTIONS_INDICES[ACHIEVEMENT_SECTION.BATTLE]
_EPIC_SECTION = ACHIEVEMENT_SECTIONS_INDICES[ACHIEVEMENT_SECTION.EPIC]
_ACTION_SECTION = ACHIEVEMENT_SECTIONS_INDICES[ACHIEVEMENT_SECTION.ACTION]
_NEAREST_ACHIEVEMENTS_COUNT = 5
_SIGNIFICANT_ACHIEVEMENTS_PER_SECTION = 3
_TOP_ACHIEVEMENTS = 9
_7X7_AVAILABLE_RANGE = range(6, 9)
_FALLOUT_AVAILABLE_RANGE = range(8, constants.MAX_VEHICLE_LEVEL + 1)
_RANKED_AVAILABLE_RANGE = (constants.MAX_VEHICLE_LEVEL,)

def _nearestComparator(x, y):
    if x.getLevelUpValue() == 1 or y.getLevelUpValue() == 1:
        if x.getLevelUpValue() == y.getLevelUpValue():
            return cmp(x.getProgressValue(), y.getProgressValue())
        if x.getLevelUpValue() == 1:
            return 1
        return -1
    return cmp(x.getProgressValue(), y.getProgressValue())


class _StatsBlockAbstract(object):

    @classmethod
    def _getAvgValue(cls, allOccursGetter, effectiveOccursGetter):
        return float(effectiveOccursGetter()) / allOccursGetter() if allOccursGetter() else None


class _StatsBlock(_StatsBlockAbstract):

    def __init__(self, dossier):
        self._stats = self._getStatsBlock(dossier)

    def getRecord(self, recordName):
        return self._stats[recordName]

    def _getStatsBlock(self, dossier):
        raise NotImplementedError

    def _getStat(self, statName):
        return self._stats[statName]


class _StatsMaxBlock(_StatsBlockAbstract):

    def __init__(self, dossier):
        self._statsMax = self._getStatsMaxBlock(dossier)

    def getRecord(self, recordName):
        return self._statsMax[recordName]

    def _getStatsMaxBlock(self, dossier):
        raise NotImplementedError

    def _getStatMax(self, statName):
        return self._statsMax[statName]


class _VehiclesStatsBlock(_StatsBlockAbstract):
    _VehiclesDossiersCut = namedtuple('VehiclesDossiersCut', ','.join(['battlesCount', 'wins', 'xp']))

    class VehiclesDossiersCut(_VehiclesDossiersCut):

        def __mul__(self, other):
            self.battlesCount += other.battlesCount
            self.wins += other.wins
            self.xp += other.xp

        def __imul__(self, other):
            return self + other

    def __init__(self, dossier):
        self._vehsList = {}
        self._markOfMasteryCut = dossier.getDossierDescr()['markOfMasteryCut']
        for intCD, cut in self._getVehDossiersCut(dossier).iteritems():
            self._vehsList[intCD] = self._packVehicle(*cut)

    def getVehicles(self):
        return self._vehsList

    def getMarksOfMastery(self):
        result = [0] * len(mark_of_mastery.MarkOfMasteryAchievement.MARK_OF_MASTERY.ALL())
        for _, markOfMastery in self._markOfMasteryCut.iteritems():
            if mark_of_mastery.isMarkOfMasteryAchieved(markOfMastery):
                result[markOfMastery - 1] += 1

        return result

    def getMarkOfMasteryForVehicle(self, intCD):
        return self._markOfMasteryCut[intCD] if intCD in self._markOfMasteryCut else mark_of_mastery.MASTERY_IS_NOT_ACHIEVED

    def getBattlesStats(self):
        return self._getBattlesStats(availableRange=range(1, constants.MAX_VEHICLE_LEVEL + 1))

    def _getBattlesStats(self, availableRange):
        vehsByType = dict(((t, 0) for t in vehicles.VEHICLE_CLASS_TAGS))
        vehsByNation = dict(((idx, 0) for idx, n in enumerate(nations.NAMES)))
        vehsByLevel = dict(((k, 0) for k in xrange(1, constants.MAX_VEHICLE_LEVEL + 1)))
        for vehTypeCompDescr, vehCut in self.getVehicles().iteritems():
            vehType = vehicles.getVehicleType(vehTypeCompDescr)
            vehsByNation[vehType.id[0]] += vehCut.battlesCount
            vehsByLevel[vehType.level] += vehCut.battlesCount
            vehsByType[set(vehType.tags & vehicles.VEHICLE_CLASS_TAGS).pop()] += vehCut.battlesCount

        for level in vehsByLevel.iterkeys():
            if level not in availableRange:
                vehsByLevel[level] = None

        return (vehsByType, vehsByNation, vehsByLevel)

    def _packVehicle(self, *args, **kwargs):
        raise NotImplementedError

    def _getVehDossiersCut(self, dossier):
        raise NotImplementedError


class _MapStatsBlock(_StatsBlockAbstract):

    class MapDossiersCut(namedtuple('MapDossiersCut', ['battlesCount', 'wins'])):

        def __mul__(self, other):
            self.battlesCount += other.battlesCount
            self.wins += other.wins

        def __imul__(self, other):
            return self + other

        @property
        def winsEfficiency(self):
            return float(self.wins) / self.battlesCount if self.battlesCount else 0

    def __init__(self, dossier):
        self._mapsList = {}
        for intCD, cut in self._getMapDossiersCut(dossier).iteritems():
            self._mapsList[intCD] = self._packMap(*cut)

    def getMaps(self):
        return self._mapsList

    def _packMap(self, *args, **kwargs):
        raise NotImplementedError

    def _getMapDossiersCut(self, dossier):
        raise NotImplementedError


class _CommonStatsBlock(_StatsBlock):

    def getBattlesCount(self):
        return self._getStat('battlesCount')


class _MaxStatsBlock(_StatsMaxBlock):

    def getMaxXp(self):
        return self._getStatMax('maxXP')

    def getMaxFrags(self):
        return self._getStatMax('maxFrags')

    def getMaxDamage(self):
        return self._getStatMax('maxDamage')


class _MaxFalloutStatsBlock(_MaxStatsBlock):

    def getMaxVictoryPoints(self):
        return self._getStatMax('maxWinPoints')


class _MaxAvatarFalloutStatsBlock(_MaxStatsBlock):

    def getMaxFragsWithAvatar(self):
        return self._getStatMax('maxFragsWithAvatar')

    def getMaxDamageWithAvatar(self):
        return self._getStatMax('maxDamageWithAvatar')


class _MaxVehicleStatsBlock(_StatsMaxBlock):

    def getMaxXpVehicle(self):
        return self._getStatMax('maxXPVehicle')

    def getMaxFragsVehicle(self):
        return self._getStatMax('maxFragsVehicle')

    def getMaxDamageVehicle(self):
        return self._getStatMax('maxDamageVehicle')


class _CommonBattleStatsBlock(_CommonStatsBlock):

    def getWinsCount(self):
        return self._getStat('wins')

    def getLossesCount(self):
        return self._getStat('losses')

    def getDrawsCount(self):
        return self.getBattlesCount() - (self.getWinsCount() + self.getLossesCount())

    def getWinsEfficiency(self):
        return self._getAvgValue(self.getBattlesCount, self.getWinsCount)

    def getLossesEfficiency(self):
        return self._getAvgValue(self.getBattlesCount, lambda : self.getBattlesCount() - self.getWinsCount())


class _BattleStatsBlock(_CommonBattleStatsBlock):

    def getXP(self):
        return self._getStat('xp')

    def getWinAndSurvived(self):
        return self._getStat('winAndSurvived')

    def getSurvivedBattlesCount(self):
        return self._getStat('survivedBattles')

    def getFragsCount(self):
        return self._getStat('frags')

    def getFrags8p(self):
        return self._getStat('frags8p')

    def getShotsCount(self):
        return self._getStat('shots')

    def getHitsCount(self):
        return self._getStat('directHits')

    def getSpottedEnemiesCount(self):
        return self._getStat('spotted')

    def getDamageDealt(self):
        return self._getStat('damageDealt')

    def getDamageReceived(self):
        return self._getStat('damageReceived')

    def getCapturePoints(self):
        return self._getStat('capturePoints')

    def getDroppedCapturePoints(self):
        return self._getStat('droppedCapturePoints')

    def getDeathsCount(self):
        return self.getBattlesCount() - self.getSurvivedBattlesCount()

    def getAvgDamage(self):
        return self._getAvgValue(self.getBattlesCount, self.getDamageDealt)

    def getAvgXP(self):
        return self._getAvgValue(self.getBattlesCount, self.getXP)

    def getAvgFrags(self):
        return self._getAvgValue(self.getBattlesCount, self.getFragsCount)

    def getAvgDamageReceived(self):
        return self._getAvgValue(self.getBattlesCount, self.getDamageReceived)

    def getAvgEnemiesSpotted(self):
        return self._getAvgValue(self.getBattlesCount, self.getSpottedEnemiesCount)

    def getHitsEfficiency(self):
        return self._getAvgValue(self.getShotsCount, self.getHitsCount)

    def getSurvivalEfficiency(self):
        return self._getAvgValue(self.getBattlesCount, self.getSurvivedBattlesCount)

    def getFragsEfficiency(self):
        return self._getAvgValue(self.getDeathsCount, self.getFragsCount)

    def getDamageEfficiency(self):
        return self._getAvgValue(self.getDamageReceived, self.getDamageDealt)


class _Battle2StatsBlock(_StatsBlockAbstract):

    def __init__(self, dossier):
        self._stats2 = self._getStats2Block(dossier)

    def getOriginalXP(self):
        return self._getStat2('originalXP')

    def getDamageAssistedTrack(self):
        return self._getStat2('damageAssistedTrack')

    def getDamageAssistedRadio(self):
        return self._getStat2('damageAssistedRadio')

    def getShotsReceived(self):
        return self._getStat2('directHitsReceived')

    def getNoDamageShotsReceived(self):
        return self._getStat2('noDamageDirectHitsReceived')

    def getPiercedReceived(self):
        return self._getStat2('piercingsReceived')

    def getHeHitsReceived(self):
        return self._getStat2('explosionHitsReceived')

    def getHeHits(self):
        return self._getStat2('explosionHits')

    def getPierced(self):
        return self._getStat2('piercings')

    def getPotentialDamageReceived(self):
        return self._getStat2('potentialDamageReceived')

    def getDamageBlockedByArmor(self):
        return self._getStat2('damageBlockedByArmor')

    def getAvgDamageBlocked(self):
        return self._getAvgValue(self.getBattlesCountVer3, self.getDamageBlockedByArmor)

    def getDamageAssistedEfficiency(self):
        value = self._getAvgValue(self.getBattlesCountVer2, lambda : self.getDamageAssistedRadio() + self.getDamageAssistedTrack())
        if value is not None:
            value = round(value)
        return value

    def getArmorUsingEfficiency(self):
        return self._getAvgValue(lambda : self.getPotentialDamageReceived() - self.getDamageBlockedByArmor(), self.getDamageBlockedByArmor)

    def getBattlesCountWithStun(self):
        return self._getStat2('battlesOnStunningVehicles')

    def getDamageAssistedStun(self):
        return self._getStat2('damageAssistedStun')

    def getAvgDamageAssistedStun(self):
        return self._getAvgValue(self.getBattlesCountWithStun, self.getDamageAssistedStun)

    def getStunNumber(self):
        return self._getStat2('stunNum')

    def getAvgStunNumber(self):
        return self._getAvgValue(self.getBattlesCountWithStun, self.getStunNumber)

    def getBattlesCountVer2(self):
        raise NotImplementedError

    def getBattlesCountVer3(self):
        raise NotImplementedError

    def getRecord(self, recordName):
        return self._stats2[recordName]

    def _getStats2Block(self, dossier):
        raise NotImplementedError

    def _getStat2(self, statName):
        return self._stats2[statName]


class _FalloutStatsBlock(_BattleStatsBlock):

    def getDeathsCount(self):
        return self._getStat('deathCount')

    def getVictoryPoints(self):
        return self._getStat('winPoints')

    def getAvgVictoryPoints(self):
        return self._getAvgValue(self.getBattlesCount, self.getVictoryPoints)

    def getFlagsDelivered(self):
        return self._getStat('flagCapture')

    def getFlagsAbsorbed(self):
        return self._getStat('soloFlagCapture')


class _AchievementsBlock(_StatsBlockAbstract):

    def __init__(self, dossier):
        self.__dossier = dossier
        self.__acceptableAchieves = self._getAcceptableAchieves()

    def __del__(self):
        self.__dossier = None
        return

    def getAchievement(self, record):
        try:
            if self.__isAchieveValid(*record):
                factory = getAchievementFactory(record, self.__dossier)
                if factory is not None:
                    return factory.create()
        except Exception:
            _logger.exception('There is exception while achievement creating %s', record)

        return

    def isAchievementInLayout(self, record):
        return record in layouts.getAchievementsLayout(self.__dossier.getDossierType())

    def getAchievements(self, isInDossier=None, showHidden=True):
        result = defaultdict(list)
        for record in layouts.getAchievementsLayout(self.__dossier.getDossierType()):
            try:
                if self.__isAchieveValid(*record):
                    factory = getAchievementFactory(record, self.__dossier)
                    if (factory and factory.isValid() and isInDossier is None or factory.isInDossier() and isInDossier or not factory.isInDossier() and not isInDossier) and factory.isValid():
                        achieve = factory.create()
                        if achieve is not None:
                            if not isinstance(factory, _SequenceAchieveFactory):
                                achieve = {achieve.getName(): achieve}
                            for a in achieve.itervalues():
                                if not a.isHidden() or showHidden:
                                    section = a.getSection()
                                    if section is None:
                                        section = getAchieveSection(record)
                                    result[section].append(a)

            except Exception:
                _logger.exception('There is exception while achievement creating %s', record)
                continue

        return tuple((sorted(result[section]) for section in ACHIEVEMENT_SECTIONS_ORDER))

    def getNearestAchievements(self):
        uncompletedAchievements = []
        for record in layouts.NEAREST_ACHIEVEMENTS:
            if self.__isAchieveValid(*record):
                a = self.getAchievement(record)
                if a is not None and a.isValid() and not a.isDone() and a.isInNear():
                    uncompletedAchievements.append(a)

        return tuple(sorted(uncompletedAchievements, cmp=_nearestComparator, reverse=True)[:_NEAREST_ACHIEVEMENTS_COUNT])

    def getSignificantAchievements(self):
        sections = self.getAchievements(isInDossier=True)
        battleAchievements = sections[_BATTLE_SECTION]
        epicAchievements = sections[_EPIC_SECTION]
        otherAchievements = itertools.chain(*itertools.ifilter(lambda x: sections.index(x) not in (_BATTLE_SECTION, _EPIC_SECTION, _ACTION_SECTION), sections))
        achievementsQuery = (battleAchievements, epicAchievements, tuple(otherAchievements))

        def mapQueryEntry(entry):
            return sorted(entry, key=lambda x: x.getWeight())[:_SIGNIFICANT_ACHIEVEMENTS_PER_SECTION]

        result = itertools.chain(*map(mapQueryEntry, achievementsQuery))
        return tuple(result)

    def getTopAchievements(self, achievesCount=_TOP_ACHIEVEMENTS):
        sections = self.getAchievements(isInDossier=True)

        def mapQueryEntry(entry):
            return sorted(entry, key=lambda x: x.getWeight())

        result = itertools.chain(*map(mapQueryEntry, itertools.chain(sections)))
        return tuple(result)[:achievesCount]

    def _getAcceptableAchieves(self):
        raise NotImplementedError

    def __isAchieveValid(self, block, name):
        return (block, name) in self.__acceptableAchieves or makeAchievesStorageName(block) in self.__acceptableAchieves and name in self.__dossier.getBlock(block)


class _RankedSeasonsStatsBlock(_StatsBlock):

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['rankedSeasons']


class _StoredRankedSeasonsStatsBlock(_RankedSeasonsStatsBlock):
    _RANK_IDX = 0
    _STEPS_COUNT_IDX = 4

    def getSeasonStepsCount(self, seasonID):
        seasonData = self.__getSeasonData(seasonID)
        return seasonData[self._STEPS_COUNT_IDX] if seasonData else 0

    def getAchievedRank(self, seasonID):
        seasonData = self.__getSeasonData(seasonID)
        return seasonData[self._RANK_IDX] if seasonData else 0

    def getSeasonsStepsCount(self):
        return self.__getTotalStatistics(self._STEPS_COUNT_IDX)

    def hadAchievedRank(self):
        statsIdx = self._RANK_IDX
        for stats in self._stats.itervalues():
            if stats[statsIdx] > 0:
                return True

        return False

    def __getTotalStatistics(self, statsIdx):
        total = 0
        for (_, cycleID), stats in self._stats.iteritems():
            if len(stats) > statsIdx:
                if cycleID == 0:
                    total += stats[statsIdx]
            _logger.error('Incorrect data format: %s', stats)

        return total

    def __getSeasonData(self, seasonID):
        finishedSeasonStats = self._stats.get((seasonID, 0))
        if not finishedSeasonStats:
            for (statSeasonID, _), stats in self._stats.iteritems():
                if statSeasonID == seasonID:
                    return stats

        return finishedSeasonStats


class _StoredVehRankedSeasonsStatsBlock(_RankedSeasonsStatsBlock):

    def getTotalRanksCount(self):
        sumPoints = 0
        for (_, cycleID), (rank, _) in self._stats.iteritems():
            if cycleID > 0:
                sumPoints += rank

        return sumPoints


class GlobalStatsBlock(_StatsBlock):

    def __init__(self, dossier):
        _StatsBlock.__init__(self, dossier)

    def getCreationTime(self):
        return self._getStat('creationTime')

    def getLastBattleTime(self):
        return self._getStat('lastBattleTime')

    def getBattleLifeTime(self):
        return self._getStat('battleLifeTime')

    def getMileage(self):
        return self._getStat('mileage')

    def getTreesCut(self):
        return self._getStat('treesCut')

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['total']


class FortGlobalStatsBlock(_StatsBlock):

    def __init__(self, dossier):
        _StatsBlock.__init__(self, dossier)

    def getCreationTime(self):
        return self._getStat('creationTime')

    def getProduction(self):
        return self._getStat('production')

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['total']


class ClubGlobalStatsBlock(_StatsBlock):

    def __init__(self, dossier):
        _StatsBlock.__init__(self, dossier)

    def getCreationTime(self):
        return self._getStat('creationTime')

    def getLastBattleTime(self):
        return self._getStat('lastBattleTime')

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['total']


class RandomStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount() - self.getBattlesCountBefore8_8()

    def getBattlesCountVer3(self):
        return self.getBattlesCount() - self.getBattlesCountBefore9_0()

    def getXpBefore8_8(self):
        return self._getStat('xpBefore8_8')

    def getBattlesCountBefore8_8(self):
        return self._getStat('battlesCountBefore8_8')

    def getBattlesCountBefore9_0(self):
        return self._getStat('battlesCountBefore9_0')

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['a15x15']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['a15x15_2']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['max15x15']

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.RANDOM)


class AccountRandomStatsBlock(RandomStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier):
        RandomStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['a15x15Cut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class EpicRandomStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount() - self.getBattlesCountBefore8_8()

    def getBattlesCountVer3(self):
        return self.getBattlesCount() - self.getBattlesCountBefore9_0()

    def getXpBefore8_8(self):
        pass

    def getBattlesCountBefore8_8(self):
        pass

    def getBattlesCountBefore9_0(self):
        pass

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['a30x30']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['a30x30']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['max30x30']

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.RANDOM)


class AccountEpicRandomStatsBlock(EpicRandomStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier):
        EpicRandomStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['a30x30Cut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class EpicBattleStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount() - self.getBattlesCountBefore8_8()

    def getBattlesCountVer3(self):
        return self.getBattlesCount() - self.getBattlesCountBefore9_0()

    def getXpBefore8_8(self):
        pass

    def getBattlesCountBefore8_8(self):
        pass

    def getBattlesCountBefore9_0(self):
        pass

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['epicBattle']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['epicBattle']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxEpicBattle']

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.EPIC_BATTLE)


class AccountEpicBattleStatsBlock(EpicBattleStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier):
        EpicBattleStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['epicBattleCut']

    def _packVehicle(self, battlesCount=0, wins=0, markOfMastery=None, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class TotalStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier, statsBlocks=None):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)
        self._statsBlocks = statsBlocks or []

    def getBattlesCountVer2(self):
        pass

    def getBattlesCountVer3(self):
        pass

    def getXpBefore8_8(self):
        pass

    def getBattlesCountBefore8_8(self):
        pass

    def getBattlesCountBefore9_0(self):
        pass

    def _getStat(self, statName):
        return self.__accumulateByStatName(statName, _BattleStatsBlock)

    def _getStat2(self, statName):
        return self.__accumulateByStatName(statName, _Battle2StatsBlock)

    def _getStatMax(self, statName):
        return self.__getMaxByStatName(statName, _MaxStatsBlock)

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.ALL)

    def _getStatsBlock(self, dossier):
        return None

    def _getStats2Block(self, dossier):
        return None

    def _getStatsMaxBlock(self, dossier):
        return None

    def __getMaxByStatName(self, statName, statsBlockType):
        result = 0
        for stats in self._statsBlocks:
            if isinstance(stats, statsBlockType):
                record = statsBlockType.getRecord(stats, statName)
                if record > result:
                    result = record

        return result

    def __accumulateByStatName(self, statName, statsBlockType):
        result = 0
        for stats in self._statsBlocks:
            if isinstance(stats, statsBlockType):
                result += statsBlockType.getRecord(stats, statName)

        return result


class AccountTotalStatsBlock(TotalStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier, statsBlocks=None):
        TotalStatsBlock.__init__(self, dossier, statsBlocks)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def _packVehicle(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def getVehicles(self):
        vehs = {}
        for stats in self._statsBlocks:
            if isinstance(stats, _VehiclesStatsBlock):
                for vTypeCompDescr, vData in stats.getVehicles().iteritems():
                    if vTypeCompDescr not in vehs:
                        vehs[vTypeCompDescr] = vData
                    vehs[vTypeCompDescr] += vData

        return vehs

    def _getVehDossiersCut(self, dossier):
        return {}


class TankmanTotalStatsBlock(_CommonStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _CommonStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['total']

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.ALL)


class CompanyStatsBlock(_BattleStatsBlock, _Battle2StatsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount() - self.getBattlesCountBefore8_9()

    def getBattlesCountVer3(self):
        return self.getBattlesCount() - self.getBattlesCountBefore9_0()

    def getXpBefore8_9(self):
        return self._getStat('xpBefore8_9')

    def getBattlesCountBefore8_9(self):
        return self._getStat('battlesCountBefore8_9')

    def getBattlesCountBefore9_0(self):
        return self._getStat('battlesCountBefore9_0')

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['company']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['company2']


class AccountCompanyStatsBlock(CompanyStatsBlock):
    pass


class ClanStatsBlock(_BattleStatsBlock, _Battle2StatsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount() - self.getBattlesCountBefore8_9()

    def getBattlesCountVer3(self):
        return self.getBattlesCount() - self.getBattlesCountBefore9_0()

    def getXpBefore8_9(self):
        return self._getStat('xpBefore8_9')

    def getBattlesCountBefore8_9(self):
        return self._getStat('battlesCountBefore8_9')

    def getBattlesCountBefore9_0(self):
        return self._getStat('battlesCountBefore9_0')

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['clan']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['clan2']


class AccountClanStatsBlock(ClanStatsBlock):
    pass


class _GlobalMapStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()


class GlobalMapCommon(_GlobalMapStatsBlock):

    def __init__(self, dossier):
        _GlobalMapStatsBlock.__init__(self, dossier)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['globalMapCommon']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['globalMapCommon']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxGlobalMapCommon']

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.RANDOM)


class _GlobalMapAccountStatsBlock(_GlobalMapStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier):
        _GlobalMapStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)


class GlobalMapMiddleBlock(_GlobalMapAccountStatsBlock):

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['globalMapMiddle']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['globalMapMiddle']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxGlobalMapMiddle']


class GlobalMapChampionBlock(_GlobalMapAccountStatsBlock):

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['globalMapChampion']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['globalMapChampion']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxGlobalMapChampion']


class GlobalMapAbsoluteBlock(_GlobalMapAccountStatsBlock):

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['globalMapAbsolute']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['globalMapAbsolute']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxGlobalMapAbsolute']


class GlobalMapTotalStatsBlock(TotalStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier, statsBlocks=None):
        TotalStatsBlock.__init__(self, dossier, statsBlocks)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['globalMapCommonCut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=None):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class Team7x7StatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount() - self.getBattlesCountBefore9_0()

    def getBattlesCountBefore9_0(self):
        return self._getStat('battlesCountBefore9_0')

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.TEAM_7X7)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['a7x7']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['a7x7']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['max7x7']


class AccountTeam7x7StatsBlock(Team7x7StatsBlock, _MaxVehicleStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier):
        Team7x7StatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def getMarksOfMastery(self):
        return UNAVAILABLE_MARKS_OF_MASTERY

    def getBattlesStats(self):
        return self._getBattlesStats(availableRange=_7X7_AVAILABLE_RANGE)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['a7x7Cut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0, originalXP=0, damage=0, damageAssistedRadio=0, damageAssistedTrack=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class HistoricalStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.HISTORICAL)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['historical']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['historical']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxHistorical']


class AccountHistoricalStatsBlock(HistoricalStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier):
        HistoricalStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def getMarksOfMastery(self):
        return UNAVAILABLE_MARKS_OF_MASTERY

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['historicalCut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class FortBattlesStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fortBattles']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['fortBattles']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxFortBattles']


class AccountFortBattlesStatsBlock(FortBattlesStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier):
        FortBattlesStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)

    def getMarksOfMastery(self):
        return UNAVAILABLE_MARKS_OF_MASTERY

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['fortBattlesCut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class FortBattlesInClanStatsBlock(FortBattlesStatsBlock):

    def __init__(self, dossier):
        FortBattlesStatsBlock.__init__(self, dossier)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fortBattlesInClan']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['fortBattlesInClan']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxFortBattlesInClan']


class FortSortiesStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fortSorties']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['fortSorties']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxFortSorties']


class AccountFortSortiesStatsBlock(FortSortiesStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier):
        FortSortiesStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)

    def getMarksOfMastery(self):
        return UNAVAILABLE_MARKS_OF_MASTERY

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['fortSortiesCut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class FortSortiesInClanStatsBlock(FortSortiesStatsBlock):

    def __init__(self, dossier):
        FortSortiesStatsBlock.__init__(self, dossier)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fortSortiesInClan']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['fortSortiesInClan']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxFortSortiesInClan']


class FortRegionBattlesStats(_CommonStatsBlock):

    def getAttackCount(self):
        return self._getStat('attackCount')

    def getDefenceCount(self):
        return self._getStat('defenceCount')

    def getSuccessDefenceCount(self):
        return self._getStat('successDefenceCount')

    def getSuccessAttackCount(self):
        return self._getStat('successAttackCount')

    def getWinsCount(self):
        return self.getSuccessDefenceCount() + self.getSuccessAttackCount()

    def getLossesCount(self):
        return self.getBattlesCount() - self.getWinsCount()

    def getWinsEfficiency(self):
        return self._getAvgValue(self.getBattlesCount, self.getWinsCount)

    def getCombatCount(self):
        return self._getStat('combatCount')

    def getCombatWins(self):
        return self._getStat('combatWins')

    def getCombatLosses(self):
        return self.getCombatCount() - self.getCombatWins()

    def getEnemyBaseCaptureCount(self):
        return self._getStat('enemyBaseCaptureCount')

    def getOwnBaseLossCount(self):
        return self._getStat('ownBaseLossCount')

    def getOwnBaseLossCountInDefence(self):
        return self._getStat('ownBaseLossCountInDefence')

    def getEnemyBaseCaptureCountInAttack(self):
        return self._getStat('enemyBaseCaptureCountInAttack')

    def getResourceCaptureCount(self):
        return self._getStat('resourceCaptureCount')

    def getResourceLossCount(self):
        return self._getStat('resourceLossCount')

    def getCaptureEnemyBuildingTotalCount(self):
        return self._getStat('captureEnemyBuildingTotalCount')

    def getLossOwnBuildingTotalCount(self):
        return self._getStat('lossOwnBuildingTotalCount')

    def getCombatWinsEfficiency(self):
        return self._getAvgValue(self.getCombatCount, self.getCombatWins)

    def getProfitFactor(self):
        return float(self.getResourceCaptureCount()) / self.getResourceLossCount() if self.getResourceLossCount() else 0

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fortBattles']


class FortRegionSortiesStats(_CommonBattleStatsBlock):

    def getMiddleBattlesCount(self):
        return self._getStat('middleBattlesCount')

    def getChampionBattlesCount(self):
        return self._getStat('championBattlesCount')

    def getAbsoluteBattlesCount(self):
        return self._getStat('absoluteBattlesCount')

    def getLootInMiddle(self):
        return self._getStat('fortResourceInMiddle')

    def getLootInChampion(self):
        return self._getStat('fortResourceInChampion')

    def getLootInAbsolute(self):
        return self._getStat('fortResourceInAbsolute')

    def getLoot(self):
        return self.getLootInMiddle() + self.getLootInChampion() + self.getLootInAbsolute()

    def getAvgLoot(self):
        return self._getAvgValue(self.getBattlesCount, self.getLoot)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fortSorties']


class Rated7x7Stats(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['rated7x7']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['rated7x7']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxRated7x7']

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.RATED_7X7)


class ClubTotalStats(_CommonBattleStatsBlock, _MapStatsBlock, _VehiclesStatsBlock, _AchievementsBlock):

    def __init__(self, dossier):
        _CommonBattleStatsBlock.__init__(self, dossier)
        _MapStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)

    def getKilledVehiclesCount(self):
        return self._getStat('killedVehicles')

    def getLostVehiclesCount(self):
        return self._getStat('lostVehicles')

    def getKilledLostVehiclesRatio(self):
        return self._getAvgValue(self.getLostVehiclesCount, self.getKilledVehiclesCount)

    def getCapturePoints(self):
        return self._getStat('capturePoints')

    def getDroppedCapturePoints(self):
        return self._getStat('droppedCapturePoints')

    def getDamageDealt(self):
        return self._getStat('damageDealt')

    def getDamageReceived(self):
        return self._getStat('damageReceived')

    def getDamageEfficiency(self):
        return self._getAvgValue(self.getDamageReceived, self.getDamageDealt)

    def getBattlesCountInAttack(self):
        return self._getStat('battlesCountInAttack')

    def getBattlesCountInDefence(self):
        return self.getBattlesCount() - self.getBattlesCountInAttack()

    def getDamageDealtInAttack(self):
        return self._getStat('damageDealtInAttack')

    def getDamageDealtInDefence(self):
        return self._getStat('damageDealtInDefence')

    def getAttackDamageEfficiency(self):
        return self._getAvgValue(self.getBattlesCountInAttack, self.getDamageDealtInAttack)

    def getDefenceDamageEfficiency(self):
        return self._getAvgValue(self.getBattlesCountInDefence, self.getDamageDealtInDefence)

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['clubBattles']

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['vehicles']

    def _packVehicle(self, battlesCount=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, -1, xp)

    def _getMapDossiersCut(self, dossier):
        return dossier.getDossierDescr()['maps']

    def _packMap(self, battlesCount=0, wins=0):
        return self.MapDossiersCut(battlesCount, wins)

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.ALL)


class _DossierStats(object):

    def _getDossierDescr(self):
        return self._getDossierItem()._getDossierDescr()

    def _getDossierItem(self):
        raise NotImplementedError


class AccountDossierStats(_DossierStats):

    def getGlobalStats(self):
        return GlobalStatsBlock(self._getDossierItem())

    def getTotalStats(self):
        return AccountTotalStatsBlock(self._getDossierItem(), (self.getRandomStats(),
         self.getTeam7x7Stats(),
         self.getHistoricalStats(),
         self.getFortBattlesStats(),
         self.getFortSortiesStats(),
         self.getRated7x7Stats(),
         self.getFalloutStats(),
         self.getRankedStats(),
         self.getEpicRandomStats()))

    def getRandomStats(self):
        return AccountRandomStatsBlock(self._getDossierItem())

    def getClanStats(self):
        return AccountClanStatsBlock(self._getDossierItem())

    def getCompanyStats(self):
        return AccountCompanyStatsBlock(self._getDossierItem())

    def getTeam7x7Stats(self):
        return AccountTeam7x7StatsBlock(self._getDossierItem())

    def getHistoricalStats(self):
        return AccountHistoricalStatsBlock(self._getDossierItem())

    def getFortBattlesInClanStats(self):
        return FortBattlesInClanStatsBlock(self._getDossierItem())

    def getFortSortiesInClanStats(self):
        return FortSortiesInClanStatsBlock(self._getDossierItem())

    def getFortBattlesStats(self):
        return AccountFortBattlesStatsBlock(self._getDossierItem())

    def getFortSortiesStats(self):
        return AccountFortSortiesStatsBlock(self._getDossierItem())

    def getRated7x7Stats(self):
        return AccountRated7x7StatsBlock(self._getDossierItem())

    def getSeasonRated7x7Stats(self, seasonID):
        return AccountSeasonRated7x7StatsBlock(self._getDossierItem().getRated7x7SeasonDossier(seasonID))

    def getGlobalMapStats(self):
        return GlobalMapTotalStatsBlock(self._getDossierItem(), (self.getGlobalMapMiddleStats(), self.getGlobalMapChampionStats(), self.getGlobalMapAbsoluteStats()))

    def getGlobalMapMiddleStats(self):
        return GlobalMapMiddleBlock(self._getDossierItem())

    def getGlobalMapChampionStats(self):
        return GlobalMapChampionBlock(self._getDossierItem())

    def getGlobalMapAbsoluteStats(self):
        return GlobalMapAbsoluteBlock(self._getDossierItem())

    def getFalloutStats(self):
        return AccountFalloutStatsBlock(self._getDossierItem())

    def getRankedStats(self):
        return TotalAccountRankedStatsBlock(self._getDossierItem())

    def getSeasonRankedStats(self, seasonKey, seasonID):
        return SeasonRankedStatsBlock(self._getDossierItem(), seasonKey, seasonID)

    def getEpicRandomStats(self):
        return AccountEpicRandomStatsBlock(self._getDossierItem())

    def getEpicBattleStats(self):
        return AccountEpicBattleStatsBlock(self._getDossierItem())


class VehicleDossierStats(_DossierStats):

    def getGlobalStats(self):
        return GlobalStatsBlock(self._getDossierItem())

    def getTotalStats(self):
        return TotalStatsBlock(self._getDossierItem(), (self.getRandomStats(),
         self.getClanStats(),
         self.getCompanyStats(),
         self.getTeam7x7Stats(),
         self.getHistoricalStats(),
         self.getFortBattlesStats(),
         self.getFortSortiesStats(),
         self.getFalloutStats(),
         self.getRankedStats(),
         self.getEpicRandomStats()))

    def getRandomStats(self):
        return RandomStatsBlock(self._getDossierItem())

    def getClanStats(self):
        return ClanStatsBlock(self._getDossierItem())

    def getCompanyStats(self):
        return CompanyStatsBlock(self._getDossierItem())

    def getTeam7x7Stats(self):
        return Team7x7StatsBlock(self._getDossierItem())

    def getRated7x7Stats(self):
        return Rated7x7Stats(self._getDossierItem())

    def getHistoricalStats(self):
        return HistoricalStatsBlock(self._getDossierItem())

    def getFortBattlesStats(self):
        return FortBattlesStatsBlock(self._getDossierItem())

    def getFortSortiesStats(self):
        return FortSortiesStatsBlock(self._getDossierItem())

    def getGlobalMapStats(self):
        return GlobalMapCommon(self._getDossierItem())

    def getFalloutStats(self):
        return FalloutStatsBlock(self._getDossierItem())

    def getRankedStats(self):
        return VehRankedStatsBlock(self._getDossierItem())

    def getEpicRandomStats(self):
        return EpicRandomStatsBlock(self._getDossierItem())

    def getEpicBattleStats(self):
        return EpicBattleStatsBlock(self._getDossierItem())


class TankmanDossierStats(_DossierStats):

    def getTotalStats(self):
        return TankmanTotalStatsBlock(self._getDossierItem())


class FortDossierStats(_DossierStats):

    def getGlobalStats(self):
        return FortGlobalStatsBlock(self._getDossierItem())

    def getBattlesStats(self):
        return FortRegionBattlesStats(self._getDossierItem())

    def getSortiesStats(self):
        return FortRegionSortiesStats(self._getDossierItem())


class ClubDossierStats(_DossierStats):

    def getGlobalStats(self):
        return ClubGlobalStatsBlock(self._getDossierItem())

    def getTotalStats(self):
        return ClubTotalStats(self._getDossierItem())


class ClubMemberDossierStats(_DossierStats):

    def getRated7x7Stats(self):
        return Rated7x7Stats(self._getDossierItem())


class AccountRated7x7StatsBlock(Rated7x7Stats, _MaxVehicleStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier):
        Rated7x7Stats.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def getMarksOfMastery(self):
        return UNAVAILABLE_MARKS_OF_MASTERY

    def getBattlesStats(self):
        return self._getBattlesStats(availableRange=_7X7_AVAILABLE_RANGE)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['rated7x7Cut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0, originalXP=0, damage=0, damageAssistedRadio=0, damageAssistedTrack=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)


class AccountSeasonRated7x7StatsBlock(AccountRated7x7StatsBlock):

    def _getVehDossiersCut(self, dossier):
        return {}


class FalloutStatsBlock(_FalloutStatsBlock, _Battle2StatsBlock, _MaxFalloutStatsBlock):

    def __init__(self, dossier):
        _FalloutStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxFalloutStatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()['fallout']

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()['fallout']

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()['maxFallout']


class AccountFalloutStatsBlock(FalloutStatsBlock, _VehiclesStatsBlock, _MaxAvatarFalloutStatsBlock):
    _FalloutVehiclesDossiersCut = namedtuple('VehiclesDossiersCut', ','.join(['battlesCount',
     'wins',
     'winPoints',
     'xp']))

    class FalloutVehiclesDossiersCut(_FalloutVehiclesDossiersCut):

        def __mul__(self, other):
            self.battlesCount += other.battlesCount
            self.wins += other.wins
            self.xp += other.xp
            self.winPoints += other.winPoints

        def __imul__(self, other):
            return self + other

    def __init__(self, dossier):
        FalloutStatsBlock.__init__(self, dossier)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxAvatarFalloutStatsBlock.__init__(self, dossier)

    def getConsumablesFragsCount(self):
        return self._getStat('avatarKills')

    def getTotalFragsCount(self):
        return self.getFragsCount() + self.getConsumablesFragsCount()

    def getAvgFrags(self):
        return self._getAvgValue(self.getBattlesCount, self.getTotalFragsCount)

    def getConsumablesDamageDealt(self):
        return self._getStat('avatarDamageDealt')

    def getTotalDamageDelt(self):
        return self.getDamageDealt() + self.getConsumablesDamageDealt()

    def getAvgDamage(self):
        return self._getAvgValue(self.getBattlesCount, self.getTotalDamageDelt)

    def getFragsEfficiency(self):
        return self._getAvgValue(self.getDeathsCount, self.getTotalFragsCount)

    def getDamageEfficiency(self):
        return self._getAvgValue(self.getDamageReceived, self.getTotalDamageDelt)

    def getMaxDamage(self):
        return self.getMaxDamageWithAvatar()

    def getMaxFrags(self):
        return self.getMaxFragsWithAvatar()

    def getMarksOfMastery(self):
        return UNAVAILABLE_MARKS_OF_MASTERY

    def getBattlesStats(self):
        return self._getBattlesStats(availableRange=_FALLOUT_AVAILABLE_RANGE)

    def getTotalVehicles(self):
        return len(self._vehsList)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['falloutCut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0, winPoints=0):
        return self.FalloutVehiclesDossiersCut(battlesCount, wins, winPoints, xp)


class RankedStatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _AchievementsBlock):

    def __init__(self, dossier, blockName, maxBlockName):
        self.__blockName = blockName
        self.__maxBlockName = maxBlockName
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)
        _AchievementsBlock.__init__(self, dossier)
        self._rankedSeasons = self._getSeasonsBlock(dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def _getSeasonsBlock(self, dossier):
        raise NotImplementedError

    def _getStatsBlock(self, dossier):
        return dossier.getDossierDescr()[self.__blockName]

    def _getStats2Block(self, dossier):
        return dossier.getDossierDescr()[self.__blockName]

    def _getStatsMaxBlock(self, dossier):
        return dossier.getDossierDescr()[self.__maxBlockName]

    def _getAcceptableAchieves(self):
        return layouts.getAchievementsByMode(ACHIEVEMENT_MODE.RANKED)


class AccountRankedStatsBlock(RankedStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier, blockName, maxBlockName):
        super(AccountRankedStatsBlock, self).__init__(dossier, blockName, maxBlockName)
        _VehiclesStatsBlock.__init__(self, dossier)

    def getStepsCount(self):
        raise NotImplementedError

    def hasAchievedRank(self):
        raise NotImplementedError

    def getStepsEfficiency(self):
        return self._getAvgValue(self.getBattlesCount, self.getStepsCount)

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)

    def _getSeasonsBlock(self, dossier):
        return _StoredRankedSeasonsStatsBlock(dossier)


class SeasonRankedStatsBlock(AccountRankedStatsBlock):

    def __init__(self, dossier, seasonKey, seasonID):
        self.__seasonKey = seasonKey
        self.__seasonID = seasonID
        super(SeasonRankedStatsBlock, self).__init__(dossier, 'ranked%s' % seasonKey, 'maxRanked%s' % seasonKey)

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['rankedCut%s' % self.__seasonKey]

    def getStepsCount(self):
        return self._rankedSeasons.getSeasonStepsCount(self.__seasonID)

    def getAchievedRank(self):
        return self._rankedSeasons.getAchievedRank(self.__seasonID)

    def hasAchievedRank(self):
        return self._rankedSeasons.hadAchievedRank()


class TotalAccountRankedStatsBlock(AccountRankedStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier):
        super(TotalAccountRankedStatsBlock, self).__init__(dossier, 'ranked', 'maxRanked')

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['rankedCut']

    def getStepsCount(self):
        return self._rankedSeasons.getSeasonsStepsCount()

    def hasAchievedRank(self):
        return self._rankedSeasons.hadAchievedRank()


class VehRankedStatsBlock(RankedStatsBlock, _VehiclesStatsBlock):

    def __init__(self, dossier):
        super(VehRankedStatsBlock, self).__init__(dossier, 'ranked', 'maxRanked')

    def getTotalRanksCount(self):
        return self._rankedSeasons.getTotalRanksCount()

    def _getVehDossiersCut(self, dossier):
        return dossier.getDossierDescr()['rankedCut']

    def _packVehicle(self, battlesCount=0, wins=0, xp=0):
        return self.VehiclesDossiersCut(battlesCount, wins, xp)

    def _getSeasonsBlock(self, dossier):
        return _StoredVehRankedSeasonsStatsBlock(dossier)
