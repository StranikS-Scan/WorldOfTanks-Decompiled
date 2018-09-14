# Embedded file name: scripts/client/gui/game_control/AOGAS.py
import Event
import BigWorld
import time
import weakref
from constants import AOGAS_TIME, ACCOUNT_ATTR
from debug_utils import LOG_ERROR, LOG_DEBUG
from enumerations import AttributeEnumItem, Enumeration
from gui.game_control.controllers import Controller
from helpers import time_utils
TIME_MODIFER = 3600
AOGAS_FORCE_START_NOTIFY = False
_DEFAULT_AOGAS_NOTIFY_TIMEOUT = 5000.0
AOGAS_NOTIFY_MSG = Enumeration('Notification message for Anti-online game addiction system', [('AOND_1', {'timeout': _DEFAULT_AOGAS_NOTIFY_TIMEOUT}),
 ('AOND_2', {'timeout': _DEFAULT_AOGAS_NOTIFY_TIMEOUT}),
 ('AOND_3', {'timeout': _DEFAULT_AOGAS_NOTIFY_TIMEOUT}),
 ('AOND_MORE_3', {'timeout': _DEFAULT_AOGAS_NOTIFY_TIMEOUT}),
 ('AOND_MORE_5', {'timeout': _DEFAULT_AOGAS_NOTIFY_TIMEOUT}),
 ('RESET', {'timeout': _DEFAULT_AOGAS_NOTIFY_TIMEOUT})], instance=AttributeEnumItem)

class AOGAS_NOTIFY_TIME(object):
    AOND_1 = 1 * TIME_MODIFER - 600
    AOND_2 = 2 * TIME_MODIFER - 600
    AOND_3 = AOGAS_TIME.REDUCED_GAIN
    AOND_5 = AOGAS_TIME.NO_GAIN


class AOGAS_NOTIFY_PERIOD(object):
    AOND_START = 5 * TIME_MODIFER / 6
    AOND_2_3 = 1 * TIME_MODIFER
    AOND_3_5 = 0.5 * TIME_MODIFER
    AOND_END = 0.25 * TIME_MODIFER


class AOGASController(Controller):

    def __init__(self, proxy):
        super(AOGASController, self).__init__(proxy)
        self.onNotifyAccount = Event.Event()
        self.__isNotifyAccount = False
        self.__lastNotifyMessages = []
        self.__aogasStartedAt = 0
        self.__isAogasEnabled = True
        self.__notificator = _AOGASNotificator(self, '_AOGASController__notifyAccount')

    def fini(self):
        self.__notificator.stop()
        self.onNotifyAccount.clear()
        super(AOGASController, self).fini()

    def onLobbyStarted(self, ctx):
        serverTime = ctx.get('aogasStartedAt')
        if serverTime is not None:
            self.__aogasStartedAt = time_utils.makeLocalServerTime(serverTime)
        else:
            self.__aogasStartedAt = time.time()
        self.__isAogasEnabled = ctx.get('isAogasEnabled', True)
        if not self.__notificator.isStarted():
            self.__requestRequiredInfo()
        return

    def onDisconnected(self):
        self.__notificator.stop()
        self.__isNotifyAccount = False
        self.__lastNotifyMessages = []

    def onLobbyInited(self, event):
        LOG_DEBUG('enableNotifyAccount ', self.__lastNotifyMessages)
        self.__isNotifyAccount = True
        for message in self.__lastNotifyMessages:
            self.onNotifyAccount(message)

        self.__lastNotifyMessages = []

    def onAvatarBecomePlayer(self):
        LOG_DEBUG('disableNotifyAccount')
        self.__isNotifyAccount = False

    def __notifyAccount(self, message, collect = False):
        if self.__isNotifyAccount:
            self.onNotifyAccount(message)
        elif collect:
            self.__lastNotifyMessages.append(message)
        else:
            self.__lastNotifyMessages = [message]

    def __requestRequiredInfo(self):
        BigWorld.player().stats.get('attrs', self.__receiveAccountAttrs)

    def __receiveAccountAttrs(self, resultID, attrs):
        if resultID < 0:
            LOG_ERROR('Server return error: ', resultID, attrs)
            return
        if self.__isAogasEnabled and ACCOUNT_ATTR.AOGAS & attrs != 0 or AOGAS_FORCE_START_NOTIFY:
            BigWorld.player().stats.get('accOnline', self.__receiveAccOnline)
        elif self.__notificator.isStarted():
            self.__notificator.stop()

    def __receiveAccOnline(self, resultID, accOnline):
        if resultID < 0:
            LOG_ERROR('Server return error: ', resultID, accOnline)
            return
        if not accOnline:
            self.__notifyAccount(AOGAS_NOTIFY_MSG.RESET)
        delta = round(time.time() - self.__aogasStartedAt)
        AOND = delta + accOnline
        LOG_DEBUG('Calculate AOND (seconds,seconds,seconds) : ', AOND, delta, accOnline)
        self.__notificator.start(AOND)


class _AOGASNotificator(object):

    def __init__(self, scope, function):
        self.__scope = weakref.ref(scope)
        self.__function = function
        self.__started = False
        self.__AOND = 0
        self.__callbackID = None
        return

    def start(self, AOND):
        if self.__started:
            return
        self.__started = True
        self.__AOND = AOND
        notificated = False
        if AOND > AOGAS_NOTIFY_TIME.AOND_1:
            prevAOND = self.__getPrevNotifyTime(AOND)
            self.__doNotify(self.__getNotifyMessages(prevAOND))
            notificated = prevAOND == AOND
        if notificated:
            notifyPeriod = self.__getNotifyPeriod(self.__AOND)
            LOG_DEBUG('AOGAS started (seconds,seconds)', self.__AOND, notifyPeriod)
            self.__callbackID = BigWorld.callback(notifyPeriod, lambda : self.__notify(notifyPeriod))
        else:
            notifyTime = self.__getNextNotifyTime(AOND)
            nextNotifyDelay = abs(notifyTime - AOND)
            LOG_DEBUG('AOGAS started (seconds,seconds,seconds)', self.__AOND, notifyTime, nextNotifyDelay)
            self.__callbackID = BigWorld.callback(nextNotifyDelay, lambda : self.__notify(nextNotifyDelay))

    def stop(self):
        self.__started = False
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def isStarted(self):
        return self.__started

    def __getNotifyPeriod(self, AOND):
        if AOND < AOGAS_NOTIFY_TIME.AOND_1:
            notifyPeriod = AOGAS_NOTIFY_PERIOD.AOND_START
        elif AOND < AOGAS_NOTIFY_TIME.AOND_3:
            notifyPeriod = AOGAS_NOTIFY_PERIOD.AOND_2_3
        elif AOND < AOGAS_NOTIFY_TIME.AOND_5:
            notifyPeriod = AOGAS_NOTIFY_PERIOD.AOND_3_5
        else:
            notifyPeriod = AOGAS_NOTIFY_PERIOD.AOND_END
        return notifyPeriod

    def __getNextNotifyTime(self, AOND):
        notifyTime = 0
        while notifyTime < AOND:
            notifyPeriod = self.__getNotifyPeriod(notifyTime)
            notifyTime += notifyPeriod

        return notifyTime

    def __getPrevNotifyTime(self, AOND):
        notifyTime = 0
        notifyPeriod = 0
        while notifyTime < AOND:
            notifyPeriod = self.__getNotifyPeriod(notifyTime)
            notifyTime += notifyPeriod

        return notifyTime - notifyPeriod

    def __getNotifyMessages(self, AOND):
        if AOND == AOGAS_NOTIFY_TIME.AOND_1:
            messages = (AOGAS_NOTIFY_MSG.AOND_1,)
        elif AOND == AOGAS_NOTIFY_TIME.AOND_2:
            messages = (AOGAS_NOTIFY_MSG.AOND_2,)
        elif AOND == AOGAS_NOTIFY_TIME.AOND_3:
            messages = (AOGAS_NOTIFY_MSG.AOND_3, AOGAS_NOTIFY_MSG.AOND_MORE_3)
        elif AOND < AOGAS_NOTIFY_TIME.AOND_5:
            messages = (AOGAS_NOTIFY_MSG.AOND_MORE_3,)
        else:
            messages = (AOGAS_NOTIFY_MSG.AOND_MORE_5,)
        return messages

    def __doNotify(self, messages):
        notifyHandler = getattr(self.__scope(), self.__function, None)
        if notifyHandler is not None and callable(notifyHandler):
            collect = len(messages) > 1
            for message in messages:
                notifyHandler(message, collect)
                LOG_DEBUG('notify (seconds, message)', self.__AOND, message)

        else:
            LOG_ERROR('Not found notify handler ', self.__scope(), self.__function)
        return

    def __notify(self, notifyPeriod):
        self.__AOND += notifyPeriod
        self.__doNotify(self.__getNotifyMessages(self.__AOND))
        notifyPeriod = self.__getNotifyPeriod(self.__AOND)
        self.__callbackID = BigWorld.callback(notifyPeriod, lambda : self.__notify(notifyPeriod))
