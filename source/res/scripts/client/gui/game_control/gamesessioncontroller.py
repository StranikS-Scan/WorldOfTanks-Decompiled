# Embedded file name: scripts/client/gui/game_control/GameSessionController.py
import time
import BigWorld
import Event
import account_shared
import constants
from adisp import process
from gui.game_control.controllers import Controller
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import time_utils
from debug_utils import *
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_itemsCache

class GameSessionController(Controller, Notifiable):
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
        self.addNotificators(PeriodicNotifier(self.__getClosestPremiumNotification, self.__notifyPremiumTime), PeriodicNotifier(lambda : self.NOTIFY_PERIOD, self.__notifyClient), PeriodicNotifier(self.__getClosestNewDayNotification, self.__notifyNewDay))
        self.__sessionStartedAt = -1
        self.__stats = None
        self.__banCallback = None
        self.__lastBanMsg = None
        self.isAdult = True
        self.isPlayTimeBlock = False
        self.__midnightBlockTime = None
        self.__playTimeBlockTime = None
        self.__doNotifyInStart = False
        self.__battles = 0
        LOG_DEBUG('GameSessionController::init')
        return

    def fini(self):
        """        Singleton finalization method """
        self._stop()
        self.onClientNotify.clear()
        self.onTimeTillBan.clear()
        self.onNewDayNotify.clear()
        self.onPremiumNotify.clear()
        self.clearNotification()
        LOG_DEBUG('GameSessionController::fini')
        super(GameSessionController, self).fini()

    @process
    def onLobbyStarted(self, ctx):
        """
        Starting new game session.
        @param ctx: lobby start context
        """
        sessionStartTime = ctx.get('sessionStartedAt', -1)
        LOG_DEBUG('GameSessionController::start', sessionStartTime)
        from gui.shared.utils.requesters import StatsRequester
        self.__stats = yield StatsRequester().request()
        self.__sessionStartedAt = sessionStartTime
        if constants.RESTRICTION_TYPE.BAN in self.__stats.restrictions:
            for ban in self.__stats.restrictions[constants.RESTRICTION_TYPE.BAN].itervalues():
                if ban.get('reason') == '#ban_reason:curfew_ban':
                    self.isAdult = False

        if self.__doNotifyInStart:
            self.__notifyClient()
        self.startNotification()
        if self.__banCallback is None:
            self.__midnightBlockTime = self.MIDNIGHT_BLOCK_TIME - time_utils.getServerRegionalTimeCurrentDay()
            playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
            self.__playTimeBlockTime = playTimeLeft - self.PLAY_TIME_LEFT_NOTIFY
            self.isPlayTimeBlock = self.__playTimeBlockTime < self.__midnightBlockTime
            self.__banCallback = BigWorld.callback(self.__getBlockTime(), self.__onBanNotifyHandler)
        g_clientUpdateManager.addCallbacks({'account': self.__onAccountChanged})
        return

    def onBattleStarted(self):
        self._stop(True)

    def onDisconnected(self):
        self._stop()

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
        curfewControl = not self.isAdult and (time_utils.getServerRegionalTimeCurrentDay() >= self.MIDNIGHT_BLOCK_TIME or time_utils.getServerRegionalTimeCurrentDay() <= time_utils.QUARTER_HOUR)
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

    @property
    def battlesCount(self):
        return self.__battles

    def incBattlesCounter(self):
        self.__battles += 1

    def _stop(self, doNotifyInStart = False):
        """ Stopping current game session """
        LOG_DEBUG('GameSessionController::stop')
        self.stopNotification()
        self.__sessionStartedAt = -1
        self.__stats = None
        self.__doNotifyInStart = doNotifyInStart
        self.__clearBanCallback()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

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

    def __getClosestPremiumNotification(self):
        premiumTime = time_utils.makeLocalServerTime(g_itemsCache.items.stats.premiumExpiryTime)
        return time_utils.getTimeDeltaFromNow(premiumTime)

    def __getBlockTime(self):
        return (self.__playTimeBlockTime if self.isPlayTimeBlock else self.__midnightBlockTime) + 5

    def __getClosestNewDayNotification(self):
        return time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()

    def __clearBanCallback(self):
        if self.__banCallback is not None:
            BigWorld.cancelCallback(self.__banCallback)
            self.__banCallback = None
        return

    def __notifyClient(self):
        playTimeLeft = None
        if self.isParentControlEnabled:
            playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
            playTimeLeft = max(playTimeLeft, 0)
        self.onClientNotify(self.sessionDuration, time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay(), playTimeLeft)
        return

    def __notifyNewDay(self):
        nextNotification = time_utils.ONE_DAY - time_utils.getServerRegionalTimeCurrentDay()
        self.onNewDayNotify(nextNotification)

    def __notifyPremiumTime(self):
        stats = g_itemsCache.items.stats
        self.onPremiumNotify(stats.isPremium, stats.attributes, stats.premiumExpiryTime)

    def __onBanNotifyHandler(self):
        """ Ban notification event handler """
        LOG_DEBUG('GameSessionController:__onBanNotifyHandler')
        banTime = time.strftime('%H:%M', time.gmtime(time.time() + self.PLAY_TIME_LEFT_NOTIFY))
        self.__lastBanMsg = (self.isPlayTimeBlock, banTime)
        self.onTimeTillBan(*self.__lastBanMsg)
        self.__banCallback = BigWorld.callback(time_utils.ONE_DAY, self.__onBanNotifyHandler)

    def __onAccountChanged(self, diff):
        if 'attrs' in diff or 'premiumExpiryTime' in diff:
            self.startNotification()
            stats = g_itemsCache.items.stats
            self.onPremiumNotify(stats.isPremium, stats.attributes, stats.premiumExpiryTime)
