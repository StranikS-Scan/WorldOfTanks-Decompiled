# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/battle_timer.py
import BigWorld
from gui.Scaleform.daapi.view.meta.EpicBattleTimerMeta import EpicBattleTimerMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_ERROR
from gui.sounds.epic_sound_constants import EPIC_SOUND, EPIC_OVERTIME_SOUND_NOTIFICATIONS
from gui.battle_control import avatar_getter

class EpicBattleTimer(EpicBattleTimerMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicBattleTimer, self).__init__()
        self.__overtimeEnd = None
        self.__overtimeCB = None
        self.__overTimeMaxTimeFac = 1
        self.__overTimeTickingPlaying = False
        self.__overTimeActive = False
        return

    def _sendTime(self, minutes, seconds):
        self.as_setTotalTimeWithSecondsS('{:02d}'.format(minutes), '{:02d}'.format(seconds), (minutes * 60 + seconds) * self.__overTimeMaxTimeFac)

    def _setColor(self):
        if not self.__overTimeTickingPlaying:
            super(EpicBattleTimer, self)._setColor()

    def _startTicking(self):
        if not self.__overTimeActive:
            super(EpicBattleTimer, self)._startTicking()

    def _triggerSoundNotification(self, notificationName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(notificationName)

    def _stopOvertimeTicking(self):
        self.__overTimeTickingPlaying = False
        self.__overTimeActive = False
        self._triggerSoundNotification(EPIC_OVERTIME_SOUND_NOTIFICATIONS.EB_OVERTIME_COUNTDOWN_STOP)
        ctrl = self.sessionProvider.dynamic.gameNotifications
        if ctrl:
            ctrl.overtimeSoundTriggered(False)

    def _populate(self):
        super(EpicBattleTimer, self)._populate()
        overTimeComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'overtimeComponent', None)
        if overTimeComp is not None:
            overTimeComp.onOvertimeStart += self.__onOvertimeStart
            overTimeComp.onOvertimeOver += self.__onOvertimeOver
            if overTimeComp.isActive:
                self.__onOvertimeStart(overTimeComp.endTime)
        else:
            LOG_ERROR('Expected OvertimeComponent not present!')
        return

    def _dispose(self):
        super(EpicBattleTimer, self)._dispose()
        overTimeComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'overtimeComponent', None)
        if overTimeComp is not None:
            overTimeComp.onOvertimeStart -= self.__onOvertimeStart
            overTimeComp.onOvertimeOver -= self.__onOvertimeOver
        return

    def __onOvertimeStart(self, endTime):
        self.as_enableOvertimeS(True)
        self.__overtimeEnd = endTime
        self.__overTimeMaxTimeFac = 1.0 / (self.__overtimeEnd - BigWorld.serverTime())
        self.__overtimeTick()
        self.__overTimeActive = True

    def __onOvertimeOver(self):
        self.as_enableOvertimeS(False)
        self.__overTimeMaxTimeFac = 1
        if self.__overtimeCB:
            BigWorld.cancelCallback(self.__overtimeCB)
            self.__overtimeCB = None
            self._stopOvertimeTicking()
            self.__overTimeTickingPlaying = False
            self.__overTimeActive = False
        return

    def __overtimeTick(self):
        diff = self.__overtimeEnd - BigWorld.serverTime()
        self.setTotalTime(diff)
        if self.__overTimeTickingPlaying is False:
            if diff <= 30.0:
                self._triggerSoundNotification(EPIC_OVERTIME_SOUND_NOTIFICATIONS.EB_OVERTIME_COUNTDOWN)
                self.__overTimeTickingPlaying = True
        if diff > 0:
            self.__overtimeCB = BigWorld.callback(1, self.__overtimeTick)
        else:
            self.__overtimeCB = None
        return
