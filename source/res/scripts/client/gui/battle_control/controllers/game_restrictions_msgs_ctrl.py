# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/game_restrictions_msgs_ctrl.py
import sys
import time
from constants import getTimeOnArena, getArenaStartTime
from messenger import MessengerEntry, g_settings
from gui.battle_control.avatar_getter import getAvatarPlayLimits, getArenaUniqueID
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.impl import backport
from gui.impl.gen import R
from helpers import time_utils

class GameRestrictionsMessagesController(Notifiable, IBattleController):
    TIME_RESERVE = 59
    THREE_MIN = time_utils.ONE_MINUTE * 3
    TWO_MIN = time_utils.ONE_MINUTE * 2
    ONE_MIN = time_utils.ONE_MINUTE
    CURFEW = 'curfew'
    DAILY = 'daily'
    WEEKLY = 'weekly'
    SESSION = 'session'

    def __init__(self):
        super(GameRestrictionsMessagesController, self).__init__()
        self.__playLimits = getAvatarPlayLimits()
        self.__minutesCount = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GAME_RESTRICTIONS_MESSAGES

    def startControl(self):
        self.addNotificators(SimpleNotifier(self.__getClosestSessionTimeNotification, self.__onBanNotifyHandler))
        self.startNotification()

    def stopControl(self):
        self.clearNotification()

    def __getDailyPlayTimeLeft(self):
        res = self.__playLimits['dailyPlayLimit']
        return res if res != -1 else sys.maxint

    def __getWeeklyPlayTimeLeft(self):
        res = self.__playLimits['weeklyPlayLimit']
        return res if res != -1 else sys.maxint

    def __getCurfew(self):
        res = self.__playLimits['curfew']
        return res if res != -1 else sys.maxint

    def __getSessionPlayTimeLeft(self):
        res = self.__playLimits['sessionLimit']
        return res if res != -1 else sys.maxint

    def __getTimeLeft(self):
        return min(self.__getCurfew(), self.__getDailyPlayTimeLeft(), self.__getWeeklyPlayTimeLeft(), self.__getSessionPlayTimeLeft())

    def __getTimeLeftPriority(self):
        return min((self.__getCurfew(), self.CURFEW), (self.__getDailyPlayTimeLeft(), self.DAILY), (self.__getWeeklyPlayTimeLeft(), self.WEEKLY), (self.__getSessionPlayTimeLeft(), self.SESSION))

    def __getNotificationStr(self):
        timeLeft, priority = self.__getTimeLeftPriority()
        if priority == self.CURFEW:
            banTime = time.strftime('%H:%M', time.localtime(getArenaStartTime(getArenaUniqueID()) + timeLeft + self.TIME_RESERVE))
            return backport.text(R.strings.messenger.chat.koreaMessage.curfew(), curfewTime=banTime, timeLeft=self.__minutesCount)
        if priority == self.WEEKLY:
            return backport.text(R.strings.messenger.chat.koreaMessage.weeklyLimit(), timeLeft=self.__minutesCount)
        if priority == self.DAILY:
            return backport.text(R.strings.messenger.chat.koreaMessage.dailyLimit(), timeLeft=self.__minutesCount)
        return backport.text(R.strings.messenger.chat.parentControlMessage.timeLimit(), timeLeft=self.__minutesCount) if priority == self.SESSION else None

    def __onBanNotifyHandler(self):
        MessengerEntry.g_instance.gui.addClientMessage(g_settings.htmlTemplates.format('battleErrorMessage', ctx={'error': self.__getNotificationStr()}))

    def __getClosestSessionTimeNotification(self):
        timeOnArena = getTimeOnArena(getArenaUniqueID())
        timeLeft = self.__getTimeLeft() - timeOnArena
        if timeLeft < 0:
            return
        banTimeLeft = 0
        self.__minutesCount = 1
        for timeNotify in (self.THREE_MIN, self.TWO_MIN, self.ONE_MIN):
            if timeLeft > timeNotify + 1:
                banTimeLeft = timeLeft - timeNotify
                self.__minutesCount = int(timeNotify // time_utils.ONE_MINUTE)
                break

        return banTimeLeft


def createGameRestrictionsMessagesController():
    return GameRestrictionsMessagesController()
