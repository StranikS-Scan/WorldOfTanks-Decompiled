# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/season_provider.py
from operator import itemgetter
import season_common
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
        now = time_utils.getServerRegionalTime()
        isCurrent, seasonInfo = season_common.getSeason(self.__getSeasonSettings().asDict(), now)
        if isCurrent:
            _, _, _, cycleID = seasonInfo
            return cycleID
        else:
            return None

    def getCurrentSeason(self):
        settings = self.__getSeasonSettings()
        now = time_utils.getServerRegionalTime()
        _, seasonInfo = season_common.getSeason(settings.asDict(), now)
        if seasonInfo:
            _, _, seasonID, _ = seasonInfo
            return self._createSeason(seasonInfo, settings.seasons.get(seasonID, {}))
        else:
            return None

    def getNextSeason(self):
        now = time_utils.getServerRegionalTime()
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
        seasonCyleInfos = season_common.getAllSeasonCycleInfos(settings.asDict(), seasonID)
        seasonData = settings.seasons.get(seasonID, {})
        if seasonData:
            cycleInfo = seasonCyleInfos[0] if seasonCyleInfos else (None,
             None,
             seasonID,
             None)
            return self._createSeason(cycleInfo, seasonData)
        else:
            return

    def isWithinSeasonTime(self, seasonID):
        settings = self.__getSeasonSettings()
        return season_common.isWithinSeasonTime(settings.asDict(), seasonID, time_utils.getCurrentLocalServerTimestamp())

    def getSeasonPassed(self):
        now = time_utils.getServerRegionalTime()
        settings = self.__getSeasonSettings()
        seasonsPassed = []
        for seasonID, season in settings.seasons.iteritems():
            endSeason = season['endSeason']
            if now >= endSeason:
                seasonsPassed.append((seasonID, endSeason))

        return seasonsPassed

    def _setSeasonSettingsProvider(self, settingsProvider):
        self.__settingsProvider = settingsProvider

    def _createSeason(self, cycleInfo, seasonData):
        return GameSeason(cycleInfo, seasonData)

    def __getSeasonSettings(self):
        return self.__settingsProvider()
