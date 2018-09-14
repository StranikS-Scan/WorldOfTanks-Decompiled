# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/GameSessionController.py
import operator
import sys
import time
import BigWorld
import Event
import account_shared
import constants
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_BAN_RESTR = constants.RESTRICTION_TYPE.BAN

def _checkForNegative(t):
    if t <= 0:
        t += time_utils.ONE_DAY
    return t


def _getSvrLocalToday():
    return time_utils.getServerRegionalTimeCurrentDay()


def _getSvrUtcToday():
    return time_utils.getServerTimeCurrentDay()


def _getSvrLocal():
    return time_utils._g_instance.serverRegionalTime


def _getSevUtc():
    return time_utils._g_instance.serverUTCTime


class GameSessionController(IGameSessionController, Notifiable):
    NOTIFY_PERIOD = time_utils.ONE_HOUR
    TIME_RESERVE = 59
    PLAY_TIME_LEFT_NOTIFY = time_utils.QUARTER_HOUR + TIME_RESERVE
    onClientNotify = Event.Event()
    onTimeTillBan = Event.Event()
    onNewDayNotify = Event.Event()
    onPremiumNotify = Event.Event()
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def init(self):
        self.addNotificators(PeriodicNotifier(self.__getClosestPremiumNotification, self.__notifyPremiumTime), PeriodicNotifier(lambda : self.NOTIFY_PERIOD, self.__notifyClient), PeriodicNotifier(self.__getClosestNewDayNotification, self.__notifyNewDay))
        self.__sessionStartedAt = -1
        self.__banCallback = None
        self.__lastBanMsg = None
        self.__curfewBlockTime = None
        self.__curfewUnblockTime = None
        self.__doNotifyInStart = False
        self.__battles = 0
        LOG_DEBUG('GameSessionController::init')
        return

    def fini(self):
        LOG_DEBUG('GameSessionController::fini')
        self._stop()
        self.onClientNotify.clear()
        self.onTimeTillBan.clear()
        self.onNewDayNotify.clear()
        self.onPremiumNotify.clear()
        self.clearNotification()
        super(GameSessionController, self).fini()

    def onLobbyStarted(self, ctx):
        LOG_DEBUG('GameSessionController::start', self.__sessionStartedAt)
        self.__sessionStartedAt = ctx.get('sessionStartedAt', -1)
        self.__curfewBlockTime, self.__curfewUnblockTime = self.__getCurfewBlockTime(self._stats.restrictions)
        if self.__doNotifyInStart:
            self.__notifyClient()
        self.startNotification()
        self.__loadBanCallback()
        g_clientUpdateManager.addCallbacks({'account': self.__onAccountChanged,
         'stats.restrictions': self.__onRestrictionsChanged,
         'stats.playLimits': self.__onPlayLimitsChanged})

    def onAvatarBecomePlayer(self):
        self._stop(doNotifyInStart=True)

    def onDisconnected(self):
        self._stop()

    def isSessionStartedThisDay(self):
        svrDaysCount = int(_getSvrLocal()) / time_utils.ONE_DAY
        clientDaysCount = int(self.__sessionStartedAt + self.__regionals().getDayStartingTime()) / time_utils.ONE_DAY
        return svrDaysCount == clientDaysCount

    def getDailyPlayTimeLeft(self):
        return self._stats.getDailyTimeLimits() - self._getDailyPlayHours()

    def getWeeklyPlayTimeLeft(self):
        return self._stats.getWeeklyTimeLimits() - self._getWeeklyPlayHours()

    @property
    def isParentControlEnabled(self):
        d, w = self._stats.getPlayTimeLimits()
        return d < time_utils.ONE_DAY or w < 7 * time_utils.ONE_DAY

    @property
    def isParentControlActive(self):
        playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
        parentControl = self.isParentControlEnabled and playTimeLeft <= self.PLAY_TIME_LEFT_NOTIFY
        notifyTime, _ = self.getCurfewBlockTime()
        banTimeLeft = min(*self.__getBlockTimeLeft())
        curfewControl = self.__curfewBlockTime is not None and banTimeLeft <= self.PLAY_TIME_LEFT_NOTIFY
        return parentControl or curfewControl

    @property
    def sessionDuration(self):
        return _getSevUtc() - self.__sessionStartedAt

    @property
    def lastBanMsg(self):
        return self.__lastBanMsg

    @property
    def battlesCount(self):
        return self.__battles

    @property
    def isAdult(self):
        return self.__curfewBlockTime is None

    @property
    def isPlayTimeBlock(self):
        playTimeLeft, curfewTimeLeft = self.__getBlockTimeLeft()
        return playTimeLeft < curfewTimeLeft

    def incBattlesCounter(self):
        self.__battles += 1

    def getCurfewBlockTime(self):
        if self.__curfewBlockTime is not None:
            blockTime = self.__curfewBlockTime - self.__regionals().getDayStartingTime()
            notifyStart = blockTime - self.PLAY_TIME_LEFT_NOTIFY
        else:
            notifyStart = blockTime = 0
        return (_checkForNegative(notifyStart), _checkForNegative(blockTime))

    def getParentControlNotificationMeta(self):
        from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
        if self.isPlayTimeBlock:
            return I18nInfoDialogMeta('koreaPlayTimeNotification')
        else:
            notifyStartTime, blockTime = self.getCurfewBlockTime()

            def formatter(t):
                return time.strftime('%H:%M', time.localtime(t))

            return I18nInfoDialogMeta('koreaParentNotification', messageCtx={'preBlockTime': formatter(notifyStartTime),
             'blockTime': formatter(blockTime)})

    @property
    def _stats(self):
        return self.itemsCache.items.stats

    def _stop(self, doNotifyInStart=False):
        LOG_DEBUG('GameSessionController::stop')
        self.stopNotification()
        self.__curfewBlockTime = None
        self.__curfewUnblockTime = None
        self.__sessionStartedAt = -1
        self.__doNotifyInStart = doNotifyInStart
        self.__clearBanCallback()
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

    def _getDailyPlayHours(self):
        if self.isSessionStartedThisDay():
            offset = _getSevUtc() - self.__sessionStartedAt
        else:
            offset = _getSvrLocal() % time_utils.ONE_DAY
        return self._stats.todayPlayHours + offset

    def _getWeeklyPlayHours(self):
        regionals = self.__regionals()
        weekDaysCount = account_shared.currentWeekPlayDaysCount(_getSevUtc(), regionals.getDayStartingTime(), regionals.getWeekStartingDay())
        return self._getDailyPlayHours() + sum(self._stats.dailyPlayHours[1:weekDaysCount])

    def __regionals(self):
        return self.lobbyContext.getServerSettings().regionals

    @classmethod
    def __getClosestNewDayNotification(cls):
        return time_utils.ONE_DAY - _getSvrLocalToday()

    def __getClosestPremiumNotification(self):
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self._stats.premiumExpiryTime))

    def __getBlockTimeLeft(self):
        playTimeLeft = min(self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft())
        if self.__curfewBlockTime is not None:
            curfewTimeLeft = self.__curfewBlockTime - _getSvrLocalToday()
        else:
            curfewTimeLeft = sys.maxint
        return (playTimeLeft, _checkForNegative(curfewTimeLeft))

    def __loadBanCallback(self, banTimeLeft=0):
        self.__clearBanCallback()
        if not banTimeLeft:
            banTimeLeft = min(*self.__getBlockTimeLeft()) - self.PLAY_TIME_LEFT_NOTIFY
        banTimeLeft = max(banTimeLeft, 0)
        LOG_DEBUG('Game session block callback', banTimeLeft)
        if banTimeLeft:
            self.__banCallback = BigWorld.callback(banTimeLeft, self.__onBanNotifyHandler)

    def __clearBanCallback(self):
        if self.__banCallback is not None:
            BigWorld.cancelCallback(self.__banCallback)
            self.__banCallback = None
        return

    def __notifyClient(self):
        if self.isParentControlEnabled:
            playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
            playTimeLeft = max(playTimeLeft, 0)
        else:
            playTimeLeft = None
        self.onClientNotify(self.sessionDuration, time_utils.ONE_DAY - _getSvrLocalToday(), playTimeLeft)
        return

    def __notifyNewDay(self):
        self.onNewDayNotify(time_utils.ONE_DAY - _getSvrLocalToday())

    def __notifyPremiumTime(self):
        stats = self._stats
        self.onPremiumNotify(stats.isPremium, stats.attributes, stats.premiumExpiryTime)

    def __onBanNotifyHandler(self):
        LOG_DEBUG('GameSessionController:__onBanNotifyHandler')
        banTime = time.strftime('%H:%M', time.localtime(time.time() + self.PLAY_TIME_LEFT_NOTIFY))
        self.__lastBanMsg = (self.isPlayTimeBlock, banTime)
        self.onTimeTillBan(*self.__lastBanMsg)
        self.__loadBanCallback()

    def __onAccountChanged(self, diff):
        if 'attrs' in diff or 'premiumExpiryTime' in diff:
            self.startNotification()
            stats = self._stats
            self.onPremiumNotify(stats.isPremium, stats.attributes, stats.premiumExpiryTime)

    def __onRestrictionsChanged(self, _):
        self.__curfewBlockTime, self.__curfewUnblockTime = self.__getCurfewBlockTime(self._stats.restrictions)
        self.__loadBanCallback()

    def __onPlayLimitsChanged(self, _):
        self.__loadBanCallback()

    @classmethod
    def __getCurfewBlockTime(cls, restrictions):
        if _BAN_RESTR in restrictions and len(restrictions[_BAN_RESTR]):
            _, ban = max(restrictions[_BAN_RESTR].items(), key=operator.itemgetter(0))
            if ban.get('reason') == '#ban_reason:curfew_ban' and 'curfew' in ban:
                return (ban['curfew'].get('from', time_utils.ONE_DAY) + cls.TIME_RESERVE, ban['curfew'].get('to', time_utils.ONE_DAY))
        return (None, None)
