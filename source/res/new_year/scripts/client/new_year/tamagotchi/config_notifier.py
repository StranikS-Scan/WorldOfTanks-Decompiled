# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/tamagotchi/config_notifier.py
from debug_utils import LOG_DEBUG_DEV_NICE, LOG_WARNING
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import getServerUTCTime
from shared_utils import findFirst
from new_year.skeletons.new_year import ITamagotchiDataProvider

class TamagotchiConfigNotifier(CallbackDelayer):
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _STOP_DELAY = -1.0

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__seasonAboutToEndId = None
        return

    @property
    def seasonAboutToStartData(self):
        nowTime = getServerUTCTime()
        seasons = self._dataProvider.config.seasons
        seasonAboutToStart = findFirst(lambda season: season.startTime - nowTime > 0, seasons)
        return (self._STOP_DELAY, 0) if seasonAboutToStart is None else (seasonAboutToStart.startTime - nowTime, seasonAboutToStart.id)

    @property
    def seasonAboutToEndData(self):
        nowTime = getServerUTCTime()
        seasons = self._dataProvider.config.seasons
        seasonAboutToEnd = findFirst(lambda season: season.endTime - nowTime > 0, seasons)
        return (self._STOP_DELAY, 0) if seasonAboutToEnd is None else (seasonAboutToEnd.endTime - nowTime, seasonAboutToEnd.id)

    def startNotify(self):
        if not self._dataProvider.isValidConfig:
            LOG_WARNING('Tamagotchi config missed or is not valid')
            self.reset()
            return
        self.__delayEndSeason()
        self.__delayStartNextSeason()

    def reset(self):
        self.destroy()

    def __delayEndSeason(self):
        delay, seasonId = self.seasonAboutToEndData
        if not seasonId:
            return
        LOG_DEBUG_DEV_NICE('Leaderboard season time to end = ', delay, ' season = ', seasonId)
        self.__seasonAboutToEndId = seasonId
        self.delayCallback(delay, self.__checkSeasonEnded)

    def __delayStartNextSeason(self):
        delay, seasonId = self.seasonAboutToStartData
        if not seasonId:
            return
        LOG_DEBUG_DEV_NICE('Leaderboard time to start next season = ', delay, ' season = ', seasonId)
        self.delayCallback(delay, self.__checkNextSeasonStarted)

    def __checkNextSeasonStarted(self):
        seasons = self._dataProvider.config.seasons
        nowTime = getServerUTCTime()
        startedSeason = findFirst(lambda season: season.startTime < nowTime < season.endTime, seasons)
        if startedSeason is None:
            return self._STOP_DELAY
        else:
            LOG_DEBUG_DEV_NICE('Leaderboard season started. Season = ', startedSeason.id)
            self._dataProvider.onNextSeasonStarted(startedSeason.id)
            self._dataProvider.updateCurrentSeason()
            delay, seasonId = self.seasonAboutToStartData
            LOG_DEBUG_DEV_NICE('Leaderboard time to start next season = ', delay, ' season = ', seasonId)
            return delay

    def __checkSeasonEnded(self):
        if not self.__seasonAboutToEndId:
            return self._STOP_DELAY
        self._dataProvider.onSeasonEnded(self.__seasonAboutToEndId)
        if self._dataProvider.config.seasons and self.__seasonAboutToEndId == self._dataProvider.config.seasons[-1].id:
            self._dataProvider.updateCurrentSeason()
        LOG_DEBUG_DEV_NICE('Leaderboard season ended. Season = ', self.__seasonAboutToEndId)
        delay, seasonId = self.seasonAboutToEndData
        self.__seasonAboutToEndId = seasonId
        LOG_DEBUG_DEV_NICE('Leaderboard season time to end = ', delay, ' season = ', seasonId)
        return delay
