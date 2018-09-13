# Embedded file name: scripts/client/gui/game_control/GameSessionController.py
import time
import BigWorld
import Event
import account_shared
import constants
from adisp import process
from helpers import time_utils
from debug_utils import *
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_itemsCache

class GameSessionController(object):
    """ Game playing time and parent controlling class. """
    NOTIFY_PERIOD = time_utils.ONE_HOUR
    PLAY_TIME_LEFT_NOTIFY = time_utils.QUARTER_HOUR
    MIDNIGHT_BLOCK_TIME = time_utils.ONE_DAY - PLAY_TIME_LEFT_NOTIFY
    onClientNotify = Event.Event()
    onTimeTillBan = Event.Event()
    onNewDayNotify = Event.Event()
    onPremiumNotify = Event.Event()

    def init(self):
        """ Singleton initialization method """
        self.__sessionStartedAt = -1
        self.__stats = None
        self.__notifyCallback = None
        self.__notifyNewDayCallback = None
        self.__banCallback = None
        self.__premiumTimeCallback = None
        self.__lastBanMsg = None
        self.isAdult = True
        self.isPlayTimeBlock = False
        self.__midnightBlockTime = None
        self.__playTimeBlockTime = None
        self.__doNotifyInStart = False
        LOG_DEBUG('GameSessionController::init')
        return

    def fini(self):
        """        Singleton finalization method """
        self.stop()
        self.onClientNotify.clear()
        self.onTimeTillBan.clear()
        self.onNewDayNotify.clear()
        self.onPremiumNotify.clear()
        LOG_DEBUG('GameSessionController::fini')

    @process
    def start(self, sessionStartTime):
        """
        Starting new game session.
        @param sessionStartTime: session start time (server time)
        """
        LOG_DEBUG('GameSessionController::start', sessionStartTime)
        from gui.shared.utils.requesters import StatsRequesterr
        self.__stats = yield StatsRequesterr().request()
        self.__sessionStartedAt = sessionStartTime
        if constants.RESTRICTION_TYPE.BAN in self.__stats.restrictions:
            for ban in self.__stats.restrictions[constants.RESTRICTION_TYPE.BAN].itervalues():
                if ban.get('reason') == '#ban_reason:curfew_ban':
                    self.isAdult = False

        if self.__doNotifyInStart:
            self.__notifyClient()
        else:
            self.__startNotifyCallback()
        if self.__notifyNewDayCallback is None:
            self.__startNewDayNotifyCallback()
        if self.__banCallback is None:
            self.__midnightBlockTime = self.MIDNIGHT_BLOCK_TIME - time_utils.getServerRegionalTimeCurrentDay()
            playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
            self.__playTimeBlockTime = playTimeLeft - self.PLAY_TIME_LEFT_NOTIFY
            self.isPlayTimeBlock = self.__playTimeBlockTime < self.__midnightBlockTime
            self.__banCallback = BigWorld.callback(self.__getBlockTime(), self.__onBanNotifyHandler)
        if self.__premiumTimeCallback is None:
            self.__startPremiumTimeNotifyCallback()
        g_clientUpdateManager.addCallbacks({'account': self.__onAccountChanged})
        return

    def stop(self, doNotifyInStart = False):
        """ Stopping current game session """
        LOG_DEBUG('GameSessionController::stop')
        self.__sessionStartedAt = -1
        self.__stats = None
        self.__doNotifyInStart = doNotifyInStart
        self.__clearBanCallback()
        self.__clearNewDayNotifyCallback()
        self.__clearNotifyCallback()
        self.__clearPremiumTimeNotifyCallback()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def isSessionStartedThisDay(self):
        """
        Is game session has been started at this day or not
        @return: <bool> flag
        """
        serverRegionalSettings = BigWorld.player().serverSettings['regional_settings']
        return int(time_utils._g_instance.serverRegionalTime) / 86400 == int(self.__sessionStartedAt + serverRegionalSettings['starting_time_of_a_new_day']) / 86400

    def getDailyPlayTimeLeft(self):
        """
        Returns value of this day playing time left in seconds
        @return: playting time left
        """
        d, _ = self.__stats.playLimits
        return d[0] - self._getDailyPlayHours()

    def getWeeklyPlayTimeLeft(self):
        """
        Returns value of this week playing time left in seconds
        @return: playting time left
        """
        _, w = self.__stats.playLimits
        return w[0] - self._getWeeklyPlayHours()

    @property
    def isParentControlEnabled(self):
        """
        Is parent control enabled. Algo has been taken
        from a_mikhailik.
        """
        d, w = self.__stats.playLimits
        return d[0] < time_utils.ONE_DAY or w[0] < 7 * time_utils.ONE_DAY

    @property
    def isParentControlActive(self):
        """
        Is parent control active now: current time between
        MIDNIGHT_BLOCK_TIME and midnight or playing time is less
        than PLAY_TIME_LEFT_NOTIFY.
        
        @return: <bool> is parent control active now
        """
        playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
        parentControl = self.isParentControlEnabled and playTimeLeft <= self.PLAY_TIME_LEFT_NOTIFY
        curfewControl = not self.isAdult and time_utils.getServerRegionalTimeCurrentDay() >= self.MIDNIGHT_BLOCK_TIME
        return parentControl or curfewControl

    @property
    def sessionDuration(self):
        """
        @return: <int> current session duration
        """
        return time_utils._g_instance.serverUTCTime - self.__sessionStartedAt

    @property
    def lastBanMsg(self):
        return self.__lastBanMsg

    def _getDailyPlayHours(self):
        """
        Returns value of this day playing time in seconds.
        @return: <int> playing time
        """
        if self.isSessionStartedThisDay():
            return self.__stats.dailyPlayHours[0] + (time_utils._g_instance.serverUTCTime - self.__sessionStartedAt)
        else:
            return self.__stats.dailyPlayHours[0] + time_utils._g_instance.serverRegionalTime % 86400

    def _getWeeklyPlayHours(self):
        """
        Returns value of this week playing time in seconds.
        @return: <int> playing time
        """
        serverRegionalSettings = BigWorld.player().serverSettings['regional_settings']
        weekDaysCount = account_shared.currentWeekPlayDaysCount(time_utils._g_instance.serverUTCTime, serverRegionalSettings['starting_time_of_a_new_day'], serverRegionalSettings['starting_day_of_a_new_week'])
        return self._getDailyPlayHours() + sum(self.__stats.dailyPlayHours[1:weekDaysCount])

    def __getBlockTime(self):
        return (self.__playTimeBlockTime if self.isPlayTimeBlock else self.__midnightBlockTime) + 5

    def __startNotifyCallback(self):
        self.__clearNotifyCallback()
        self.__notifyCallback = BigWorld.callback(self.NOTIFY_PERIOD, self.__notifyClient)

    def __startNewDayNotifyCallback(self):
        self.__clearNewDayNotifyCallback()
        nextNotification = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
        self.__notifyNewDayCallback = BigWorld.callback(nextNotification, self.__notifyNewDay)

    def __startPremiumTimeNotifyCallback(self):
        self.__clearPremiumTimeNotifyCallback()
        premiumTime = time_utils.makeLocalServerTime(g_itemsCache.items.stats.premiumExpiryTime)
        delta = time_utils.getTimeDeltaFromNow(premiumTime)
        if delta > time_utils.ONE_DAY:
            period = time_utils.ONE_DAY
        elif delta > time_utils.ONE_HOUR:
            period = time_utils.ONE_HOUR
        else:
            return
        nextNotification = delta % period or period
        self.__premiumTimeCallback = BigWorld.callback(nextNotification, self.__notifyPremiumTime)

    def __clearNotifyCallback(self):
        if self.__notifyCallback is not None:
            BigWorld.cancelCallback(self.__notifyCallback)
            self.__notifyCallback = None
        return

    def __clearNewDayNotifyCallback(self):
        if self.__notifyNewDayCallback is not None:
            BigWorld.cancelCallback(self.__notifyNewDayCallback)
            self.__notifyNewDayCallback = None
        return

    def __clearBanCallback(self):
        if self.__banCallback is not None:
            BigWorld.cancelCallback(self.__banCallback)
            self.__banCallback = None
        return

    def __clearPremiumTimeNotifyCallback(self):
        if self.__premiumTimeCallback is not None:
            BigWorld.cancelCallback(self.__premiumTimeCallback)
            self.__premiumTimeCallback = None
        return

    def __notifyClient(self):
        playTimeLeft = None
        if self.isParentControlEnabled:
            playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
            playTimeLeft = max(playTimeLeft, 0)
        self.onClientNotify(self.sessionDuration, time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay(), playTimeLeft)
        self.__startNotifyCallback()
        return

    def __notifyNewDay(self):
        nextNotification = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
        self.onNewDayNotify(nextNotification)
        self.__startNewDayNotifyCallback()

    def __notifyPremiumTime(self):
        stats = g_itemsCache.items.stats
        self.onPremiumNotify(stats.isPremium, stats.attributes, stats.premiumExpiryTime)
        self.__startPremiumTimeNotifyCallback()

    def __onBanNotifyHandler(self):
        """ Ban notification event handler """
        LOG_DEBUG('GameSessionController:__onBanNotifyHandler')
        banTime = time.strftime('%H:%M', time.gmtime(time.time() + self.PLAY_TIME_LEFT_NOTIFY))
        self.__lastBanMsg = (self.isPlayTimeBlock, banTime)
        self.onTimeTillBan(*self.__lastBanMsg)
        self.__banCallback = BigWorld.callback(time_utils.ONE_DAY, self.__onBanNotifyHandler)

    def __onAccountChanged(self, diff):
        if 'attrs' in diff or 'premiumExpiryTime' in diff:
            self.__startPremiumTimeNotifyCallback()
            stats = g_itemsCache.items.stats
            self.onPremiumNotify(stats.isPremium, stats.attributes, stats.premiumExpiryTime)
