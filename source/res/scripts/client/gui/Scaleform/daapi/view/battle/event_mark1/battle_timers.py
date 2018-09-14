# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/battle_timers.py
from gui.shared.lock import Lock
from gui.battle_control.battle_constants import BATTLE_SYNC_LOCKS
from gui.Scaleform.daapi.view.battle.event_mark1.common import playMark1AtBaseWarningSound
from gui.Scaleform.daapi.view.battle.shared import battle_timers
from gui.battle_control import g_sessionProvider
from constants import ARENA_PERIOD
_NOTIFICATION_DELAY_TIMEOUT = 3

class Mark1BattleTimer(battle_timers.BattleTimer):

    def __init__(self):
        super(Mark1BattleTimer, self).__init__()
        self.__soundLock = Lock(BATTLE_SYNC_LOCKS.BATTLE_MARK1_AT_BASE_SOUND_LOCK)
        self.__eventsLock = Lock(BATTLE_SYNC_LOCKS.MARK1_EVENT_NOTIFICATIONS)
        self.__notificationLocked = self.__eventsLock.tryLock()
        self.__notificationDelay = _NOTIFICATION_DELAY_TIMEOUT

    def setTotalTime(self, totalTime):
        if self.__notificationLocked:
            periodCtrl = g_sessionProvider.shared.arenaPeriod
            if periodCtrl is not None:
                period = periodCtrl.getPeriod()
                if period == ARENA_PERIOD.BATTLE:
                    self.__notificationDelay -= 1
                if self.__notificationDelay <= 0:
                    self.__eventsLock.unlock()
                    self.__notificationLocked = False
            else:
                self.__eventsLock.unlock()
                self.__notificationLocked = False
        super(Mark1BattleTimer, self).setTotalTime(totalTime)
        return

    def _dispose(self):
        self.__soundLock.dispose()
        self.__eventsLock.dispose()
        super(Mark1BattleTimer, self)._dispose()

    def _callWWISE(self, wwiseEventName):
        if wwiseEventName == battle_timers._WWISE_EVENTS.BATTLE_ENDING_SOON:
            playMark1AtBaseWarningSound(self.__soundLock)
        super(Mark1BattleTimer, self)._callWWISE(wwiseEventName)
