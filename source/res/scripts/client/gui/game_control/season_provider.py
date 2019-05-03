# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/season_provider.py
from operator import itemgetter
import season_common
from shared_utils import first
from skeletons.gui.game_control import ISeasonProvider
from helpers import time_utils
from season_common import GameSeason

class SeasonProvider(ISeasonProvider):

    def __init__(self):
        self.__settingsProvider = None
        return

    def hasAnySeason(self):
        return bool(self.__getSeasonSettings().seasons)

    def getCurrentCycleID(self):
        now = self.__getNow()
        isCurrent, seasonInfo = season_common.getSeason(self.__getSeasonSettings().asDict(), now)
        if isCurrent:
            _, _, _, cycleID = seasonInfo
            return cycleID
        else:
            return None

    def getCurrentSeason(self):
        now = self.__getNow()
        for seasonID, seasonData in self.__getSeasonSettings().seasons.iteritems():
            if seasonData['startSeason'] <= now < seasonData['endSeason']:
                currCycleInfo = (None,
                 None,
                 seasonID,
                 None)
                for cycleID, cycleTimes in seasonData['cycles'].iteritems():
                    if cycleTimes['start'] <= now < cycleTimes['end']:
                        currCycleInfo = (cycleTimes['start'],
                         cycleTimes['end'],
                         seasonID,
                         cycleID)

                return self._createSeason(currCycleInfo, seasonData)

        return

    def getNextSeason(self):
        now = self.__getNow()
        settings = self.__getSeasonSettings()
        seasonsComing = []
        for seasonID, season in settings.seasons.iteritems():
            startSeason = season['startSeason']
            if now < startSeason:
                seasonsComing.append((seasonID, startSeason))

        if seasonsComing:
            seasonID, _ = min(seasonsComing, key=itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

    def getPreviousSeason(self):
        seasonsPassed = self.getSeasonPassed()
        if seasonsPassed:
            seasonID, _ = max(seasonsPassed, key=itemgetter(1))
            return self.getSeason(seasonID)
        else:
            return None

    def getSeason(self, seasonID):
        settings = self.__getSeasonSettings()
        seasonCycleInfos = season_common.getAllSeasonCycleInfos(settings.asDict(), seasonID)
        seasonData = settings.seasons.get(seasonID, {})
        if seasonData:
            cycleInfo = first(seasonCycleInfos, (None,
             None,
             seasonID,
             None))
            return self._createSeason(cycleInfo, seasonData)
        else:
            return

    def isWithinSeasonTime(self, seasonID):
        settings = self.__getSeasonSettings()
        return season_common.isWithinSeasonTime(settings.asDict(), seasonID, self.__getNow())

    def getSeasonPassed(self):
        now = self.__getNow()
        settings = self.__getSeasonSettings()
        seasonsPassed = []
        for seasonID, season in settings.seasons.iteritems():
            endSeason = season['endSeason']
            if now >= endSeason:
                seasonsPassed.append((seasonID, endSeason))

        return seasonsPassed

    def getClosestStateChangeTime(self):
        season = self.getCurrentSeason()
        now = self.__getNow()
        if season is not None:
            if season.hasActiveCycle(now):
                return season.getCycleEndDate()
            return season.getCycleStartDate() or season.getEndDate()
        else:
            season = self.getNextSeason()
            return season.getStartDate() if season else 0

    def _setSeasonSettingsProvider(self, settingsProvider):
        self.__settingsProvider = settingsProvider

    def _createSeason(self, cycleInfo, seasonData):
        return GameSeason(cycleInfo, seasonData)

    def __getSeasonSettings(self):
        return self.__settingsProvider()

    @staticmethod
    def __getNow():
        return time_utils.getCurrentLocalServerTimestamp()
