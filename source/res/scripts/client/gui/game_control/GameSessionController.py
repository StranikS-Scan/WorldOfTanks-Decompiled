# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/GameSessionController.py
import sys
import time
import typing
import BigWorld
import Event
import account_shared
import constants
from constants import SECONDS_IN_DAY
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier, SimpleNotifier, AcyclicNotifier
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from skeletons.gui.shared.utils.requesters import IGameRestrictionsRequester
_BAN_RESTR = constants.RESTRICTION_TYPE.BAN

def _checkForNegative(t):
    if t <= 0:
        t += time_utils.ONE_DAY
    return t


def _checkForThisDay(t):
    if t >= time_utils.ONE_DAY:
        t -= time_utils.ONE_DAY
    return t


def _getSvrLocalToday():
    return time_utils.getServerRegionalTimeCurrentDay()


def _getSvrUtcToday():
    return time_utils.getServerTimeCurrentDay()


def _getSvrLocal():
    return time_utils._g_instance.serverRegionalTime


def _getSevUtc():
    return time_utils.getServerUTCTime()


class GameSessionController(IGameSessionController, IGlobalListener, Notifiable):
    NOTIFY_PERIOD = time_utils.ONE_HOUR
    TIME_RESERVE = 59
    PLAY_TIME_LEFT_NOTIFY = time_utils.QUARTER_HOUR + TIME_RESERVE
    TIME_LEFT_NOTIFY_FROM_EPIC = time_utils.HALF_HOUR + TIME_RESERVE
    onClientNotify = Event.Event()
    onTimeTillBan = Event.Event()
    onNewDayNotify = Event.Event()
    onPremiumNotify = Event.Event()
    onPremiumTypeChanged = Event.Event()
    onParentControlNotify = Event.Event()
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def init(self):
        self.__timeTillKickNotifier = AcyclicNotifier(self.__getClosestTimeTillKickNotification, self.__notifyTimeTillKick)
        self.addNotificators(PeriodicNotifier(self.__getClosestPremiumNotification, self.__notifyPremiumTime), SimpleNotifier(self.__getClosestSessionTimeNotification, self.__notifyClient), PeriodicNotifier(self.__getClosestNewDayNotification, self.__notifyNewDay), self.__timeTillKickNotifier)
        self.__sessionStartedAt = -1
        self.__banCallback = None
        self.__lastBanMsg = None
        self.__curfewBlockTime = None
        self.__curfewUnblockTime = None
        self.__doNotifyInStart = False
        self.__battles = 0
        self.__lastNotifyTime = None
        LOG_DEBUG('GameSessionController::init')
        return

    def fini(self):
        LOG_DEBUG('GameSessionController::fini')
        self._stop()
        self.onClientNotify.clear()
        self.onTimeTillBan.clear()
        self.onNewDayNotify.clear()
        self.onPremiumNotify.clear()
        self.onParentControlNotify.clear()
        self.clearNotification()
        if self.__timeTillKickNotifier is not None:
            self.__timeTillKickNotifier = None
        super(GameSessionController, self).fini()
        return

    def onLobbyStarted(self, ctx):
        self.__sessionStartedAt = ctx.get('aogasStartedAt', -1)
        LOG_DEBUG('GameSessionController::start', self.__sessionStartedAt)

    def onLobbyInited(self, event):
        if self.__lastNotifyTime is None:
            self.__lastNotifyTime = time_utils.getCurrentTimestamp()
        self.__curfewBlockTime, self.__curfewUnblockTime = self.__getCurfewBlockTime(self._stats.restrictions)
        if self.__doNotifyInStart:
            self.__notifyClient()
        self.startNotification()
        self.__loadBanCallback()
        g_clientUpdateManager.addCallbacks({'premium': self.__onAccountChanged,
         'stats.restrictions': self.__onRestrictionsChanged,
         'stats.playLimits': self.__onPlayLimitsChanged,
         'cache.gameRestrictions.session': self.__onParentControlChanged,
         'cache.gameRestrictions.session_r': self.__onParentControlChanged})
        self.startGlobalListening()
        return

    def onAvatarBecomePlayer(self):
        self._stop(doNotifyInStart=True)

    def onDisconnected(self):
        self._stop()
        self.__lastNotifyTime = None
        self.__lastBanMsg = None
        return

    def isSessionStartedThisDay(self):
        svrDaysCount = int(_getSvrLocal()) / time_utils.ONE_DAY
        clientDaysCount = int(self.__sessionStartedAt - self.__regionals().getDayStartingTime()) / time_utils.ONE_DAY
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
        playTimeForBattle = self.getPlayTimeNotify()
        parentControl = self.isParentControlEnabled and playTimeLeft <= playTimeForBattle
        _, _ = self.getCurfewBlockTime()
        banTimeLeft = min(*self.__getBlockTimeLeft())
        curfewControl = self.__curfewBlockTime is not None and banTimeLeft <= playTimeForBattle
        gameRestrictions = self._gameRestrictions.hasSessionLimit and self._gameRestrictions.getKickAt() - _getSevUtc() <= playTimeForBattle
        return parentControl or curfewControl or gameRestrictions

    @prbEntityProperty
    def prbEntity(self):
        pass

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

    def onPrbEntitySwitched(self):
        if self.__timeTillKickNotifier is not None:
            self.__timeTillKickNotifier.startNotification()
        return

    def incBattlesCounter(self):
        self.__battles += 1

    def getPlayTimeNotify(self):
        return self.TIME_LEFT_NOTIFY_FROM_EPIC if self.prbEntity and self.prbEntity.getQueueType() == constants.QUEUE_TYPE.EPIC else self.PLAY_TIME_LEFT_NOTIFY

    def getCurfewBlockTime(self):
        if self.__curfewBlockTime is not None:
            blockTime = self.__curfewBlockTime
            notifyStart = blockTime - self.getPlayTimeNotify()
        else:
            notifyStart = blockTime = 0
        return (_checkForNegative(notifyStart), _checkForNegative(blockTime))

    def getParentControlNotificationMeta(self):
        from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta
        if self.isPlayTimeBlock:
            return I18nInfoDialogMeta('koreaPlayTimeNotification')
        elif self.__curfewBlockTime is not None:
            notifyStartTime, blockTime = self.getCurfewBlockTime()

            def formatter(t):
                return time.strftime('%H:%M', time.localtime(t))

            return I18nInfoDialogMeta('koreaParentNotification', messageCtx={'preBlockTime': formatter(notifyStartTime),
             'blockTime': formatter(blockTime)})
        else:
            return

    @property
    def _stats(self):
        return self.itemsCache.items.stats

    @property
    def _gameRestrictions(self):
        return self.itemsCache.items.gameRestrictions

    def _stop(self, doNotifyInStart=False):
        LOG_DEBUG('GameSessionController::stop')
        self.stopNotification()
        self.__curfewBlockTime = None
        self.__curfewUnblockTime = None
        self.__sessionStartedAt = -1
        self.__doNotifyInStart = doNotifyInStart
        self.__clearBanCallback()
        self.stopGlobalListening()
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
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self._stats.activePremiumExpiryTime))

    def __getClosestSessionTimeNotification(self):
        delay = self.NOTIFY_PERIOD
        if self.__lastNotifyTime is not None:
            timeSinceLastNotify = time_utils.getCurrentTimestamp() - self.__lastNotifyTime
            delay -= timeSinceLastNotify
            if delay <= 0:
                delay = 1
        return delay

    def __getClosestTimeTillKickNotification(self):
        delay = 0
        if self._gameRestrictions.getKickAt():
            playTimeForBattle = self.getPlayTimeNotify()
            delay = max(self._gameRestrictions.getKickAt() - _getSevUtc() - playTimeForBattle, 1)
        return delay

    def __getBlockTimeLeft(self):
        playTimeLeft = min(self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft())
        if self.__curfewBlockTime is not None:
            curfewTimeLeft = self.__curfewBlockTime - _getSvrUtcToday()
        else:
            curfewTimeLeft = sys.maxint
        return (playTimeLeft, _checkForNegative(curfewTimeLeft))

    def __loadBanCallback(self, banTimeLeft=0):
        self.__clearBanCallback()
        if not banTimeLeft:
            banTimeLeft = min(*self.__getBlockTimeLeft()) - self.PLAY_TIME_LEFT_NOTIFY
        banTimeLeft = max(banTimeLeft, 1)
        LOG_DEBUG('Game session block callback', banTimeLeft)
        if banTimeLeft and self.__lastBanMsg is None:
            self.__banCallback = BigWorld.callback(banTimeLeft, self.__onBanNotifyHandler)
        return

    def __clearBanCallback(self):
        if self.__banCallback is not None:
            BigWorld.cancelCallback(self.__banCallback)
            self.__banCallback = None
        return

    def __notifyClient(self):
        self.__lastNotifyTime = time_utils.getCurrentTimestamp()
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
        self.onPremiumNotify(stats.isPremium, stats.attributes, stats.activePremiumExpiryTime)

    def __notifyTimeTillKick(self):
        messageText = backport.text(R.strings.system_messages.gameSessionControl.parentControl.kickTime(), kickTime=backport.getShortTimeFormat(self._gameRestrictions.getKickAt()))
        SystemMessages.pushMessage(messageText, SM_TYPE.Warning, NotificationPriorityLevel.HIGH)

    def __notifyParentControlChanged(self, timeLimit):
        msgList = [backport.text(R.strings.system_messages.gameSessionControl.parentControl.settingsChanged())]
        if timeLimit:
            msgList.append(backport.text(R.strings.system_messages.gameSessionControl.parentControl.timeLimit(), timeLimit=backport.getDateTimeFormat(timeLimit)))
        else:
            msgList.append(backport.text(R.strings.system_messages.gameSessionControl.parentControl.noTimeLimit()))
        messageText = text_styles.concatStylesToMultiLine(*msgList)
        SystemMessages.pushMessage(messageText, SM_TYPE.Warning, NotificationPriorityLevel.HIGH)

    def __onBanNotifyHandler(self):
        LOG_DEBUG('GameSessionController:__onBanNotifyHandler')
        playTimeLeft = min([self.getDailyPlayTimeLeft(), self.getWeeklyPlayTimeLeft()])
        playTimeLeft = max(playTimeLeft, 0)
        banTime = time.strftime('%H:%M', time.localtime(time_utils.getCurrentTimestamp() + playTimeLeft))
        self.__lastBanMsg = (self.isPlayTimeBlock, banTime)
        self.onTimeTillBan(*self.__lastBanMsg)
        self.__loadBanCallback()

    def __onAccountChanged(self, diff):
        self.startNotification()
        stats = self._stats
        self.onPremiumNotify(stats.isPremium, stats.attributes, stats.activePremiumExpiryTime)
        if 'premMask' in diff:
            self.onPremiumTypeChanged(stats.activePremiumType)

    def __onRestrictionsChanged(self, _):
        self.__curfewBlockTime, self.__curfewUnblockTime = self.__getCurfewBlockTime(self._stats.restrictions)
        self.__lastBanMsg = None
        self.__loadBanCallback()
        return

    def __onPlayLimitsChanged(self, _):
        self.__lastBanMsg = None
        self.__loadBanCallback()
        return

    def __onParentControlChanged(self, diff):
        if diff and 'kick_at' not in diff:
            return
        if not diff:
            timeLimit = 0
        else:
            timeLimit = self._gameRestrictions.getKickAt()
        self.onParentControlNotify()
        self.__notifyParentControlChanged(timeLimit)
        self.__timeTillKickNotifier.startNotification()

    @classmethod
    def __getCurfewBlockTime(cls, restrictions):
        if _BAN_RESTR in restrictions and restrictions[_BAN_RESTR]:
            ban = cls.__getNearestCurfew(restrictions[_BAN_RESTR])
            if ban is not None and ban.get('reason') is not None:
                return (ban['curfew'].get('from', time_utils.ONE_DAY) + cls.TIME_RESERVE, ban['curfew'].get('to', time_utils.ONE_DAY))
        return (None, None)

    @classmethod
    def __getNearestCurfew(cls, restrictions):
        curfewNearest = None
        curTime = int(time_utils.getCurrentLocalServerTimestamp())
        elapsedSecondsOfCurDay = curTime % SECONDS_IN_DAY
        curfewStarts = lambda cFrom, curDay: cFrom - curDay if cFrom > curDay else cFrom - curDay + SECONDS_IN_DAY
        for _, restr in restrictions.items():
            if 'curfew' not in restr:
                continue
            if restr is None:
                continue
            curfew = restr['curfew']
            curfewFrom = curfew['from']
            if curfewNearest is None or curfewStarts(curfewFrom, elapsedSecondsOfCurDay) < curfewStarts(curfewNearest['curfew']['from'], elapsedSecondsOfCurDay):
                curfewNearest = restr

        return curfewNearest
