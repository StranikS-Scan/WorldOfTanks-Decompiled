# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_helpers/stats_composer.py
from collections import namedtuple
import time
import typing
from gui.ranked_battles.constants import RankedDossierKeys, ARCHIVE_SEASON_ID, ZERO_DIVISION_ID
from helpers import dependency
from skeletons.gui.shared import IItemsCache
EfficiencyStamp = namedtuple('EfficiencyStamp', 'efficiency, time')

class RankedBattlesStatsComposer(object):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__settings', '__currentSeason')

    def __init__(self, settings, currentSeason):
        super(RankedBattlesStatsComposer, self).__init__()
        self.__settings = settings
        self.__currentSeason = currentSeason

    @property
    def amountBattles(self):
        return sum((division.get('battles', 0) for division in self.divisionsStats.itervalues())) if self.divisionsStats is not None else self.__getSeasonDossier().getBattlesCount()

    @property
    def amountBattlesInLeagues(self):
        return sum((self.divisionsStats.get(divisionID, {}).get('battles', 0) for divisionID, division in self.__settings.divisions.iteritems() if division['isLeague'])) if self.divisionsStats is not None and self.__settings is not None else None

    @property
    def amountSteps(self):
        return self.__getSeasonDossier().getStepsCount()

    @property
    def amountStepsInLeagues(self):
        if self.divisionsStats is not None and self.amountSteps is not None:
            result = 0
            for divisionID, division in self.__settings.divisions.iteritems():
                if division['isLeague']:
                    result += self.divisionsStats.get(divisionID, {}).get('rankChanges', 0)

        else:
            result = None
        return result

    @property
    def bonusBattlesCount(self):
        return self.itemsCache.items.ranked.persistentBonusBattles + self.itemsCache.items.ranked.dailyBonusBattles

    @property
    def persistentBonusBattles(self):
        return self.itemsCache.items.ranked.persistentBonusBattles

    @property
    def dailyBonusBattles(self):
        return self.itemsCache.items.ranked.dailyBonusBattles

    @property
    def dailyBonusBattlesIncome(self):
        steps = self.divisionsStats.get(ZERO_DIVISION_ID, {}).get('stepsCount', 0)
        settings = self.__settings.leaguesBonusBattles
        bonusBattles = {item['battlesCount']:item['steps'] for item in settings if item['steps'] <= steps}
        return max(bonusBattles or (0,))

    @property
    def cachedSeasonEfficiency(self):
        efficiencyStamp = self.itemsCache.items.ranked.seasonEfficiencyStamp
        efficiency = efficiencyStamp.get('efficiency', self.currentSeasonEfficiency.efficiency)
        timeStamp = efficiencyStamp.get('timestamp', time.time())
        return EfficiencyStamp(efficiency, timeStamp)

    @property
    def currentSeasonEfficiency(self):
        if self.amountBattles:
            efficiency = float(self.__getSeasonDossier().getStepsCount()) / self.amountBattles
        else:
            efficiency = None
        return EfficiencyStamp(efficiency, time.time())

    @property
    def currentSeasonEfficiencyDiff(self):
        result = None
        if self.currentSeasonEfficiency.efficiency is not None and self.cachedSeasonEfficiency.efficiency is not None:
            result = self.currentSeasonEfficiency.efficiency - self.cachedSeasonEfficiency.efficiency
        return result

    @property
    def divisionsStats(self):
        return self.itemsCache.items.ranked.divisionsStats

    @property
    def hasSettings(self):
        return self.__settings is not None

    def clear(self):
        self.__settings = None
        self.__currentSeason = None
        return

    def getDivisionEfficiencyPercent(self, divisionsID):
        currentDivisionEfficiency = None
        if self.divisionsStats is not None:
            currentDivisionStats = self.divisionsStats.get(divisionsID)
            if currentDivisionStats:
                rankChanges = currentDivisionStats.get('rankChanges', 0)
                battles = currentDivisionStats.get('battles', 0)
                if battles:
                    currentDivisionEfficiency = rankChanges / float(battles)
        return currentDivisionEfficiency

    def __getSeasonDossier(self):
        seasonKey = RankedDossierKeys.ARCHIVE
        seasonID = ARCHIVE_SEASON_ID
        if self.__currentSeason is not None:
            seasonKey = RankedDossierKeys.SEASON % self.__currentSeason.getNumber()
            seasonID = self.__currentSeason.getSeasonID()
        return self.itemsCache.items.getAccountDossier().getSeasonRankedStats(seasonKey, seasonID)
