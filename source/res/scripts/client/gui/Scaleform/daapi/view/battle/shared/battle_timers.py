# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/battle_timers.py
import BigWorld
import SoundGroups
import CommandMapping
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.BattleTimerMeta import BattleTimerMeta
from gui.Scaleform.daapi.view.meta.PrebattleTimerMeta import PrebattleTimerMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import COUNTDOWN_STATE, BATTLE_CTRL_ID
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers import dependency
from helpers import i18n
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.Scaleform.locale.PREBATTLE import PREBATTLE
from gui.shared.utils.key_mapping import getReadableKey
from helpers.i18n import makeString as _ms
_TIMER_ANIMATION_SHIFT = 0.4

class _WWISE_EVENTS(object):
    BATTLE_ENDING_SOON = 'time_buzzer_02'
    COUNTDOWN_TICKING = 'time_countdown'
    STOP_TICKING = 'time_countdown_stop'


_BATTLE_END_TIME = 0
_STATE_TO_MESSAGE = {COUNTDOWN_STATE.WAIT: INGAME_GUI.TIMER_WAITING,
 COUNTDOWN_STATE.START: INGAME_GUI.TIMER_STARTING,
 COUNTDOWN_STATE.STOP: INGAME_GUI.TIMER_STARTED}

class PreBattleTimer(PrebattleTimerMeta, IAbstractPeriodView, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self._state = COUNTDOWN_STATE.WAIT
        self._battleTypeStr = None
        self.__timeLeft = None
        self.__callbackID = None
        self.__arenaPeriod = None
        super(PreBattleTimer, self).__init__()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def updateBattleCtx(self, battleCtx):
        self._battleTypeStr = battleCtx.getArenaDescriptionString(isInBattle=False)
        self.as_setMessageS(self._getMessage())
        self.as_setWinConditionTextS(battleCtx.getArenaWinString())

    def setPeriod(self, period):
        if self.__arenaPeriod is None and period == ARENA_PERIOD.BATTLE:
            self.as_hideAllS(False)
        self.__arenaPeriod = period
        return

    def setCountdown(self, state, timeLeft):
        self.__timeLeft = timeLeft
        if self._state != state:
            self._state = state
            self.as_setMessageS(self._getMessage())
        if state == COUNTDOWN_STATE.WAIT:
            self.__clearTimeShiftCallback()
            self.as_setTimerS(0)
        else:
            self.__setTimeShitCallback()

    def hideCountdown(self, state, speed):
        self.as_setMessageS(i18n.makeString(_STATE_TO_MESSAGE[state]))
        self.__clearTimeShiftCallback()
        self.as_hideAllS(speed != 0)

    def _getMessage(self):
        if self._state == COUNTDOWN_STATE.WAIT:
            msg = _STATE_TO_MESSAGE[self._state]
        else:
            msg = self._battleTypeStr
        return i18n.makeString(msg)

    def _populate(self):
        super(PreBattleTimer, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        CommandMapping.g_instance.onMappingChanged += self.__onMappingChanged
        self.__onMappingChanged()

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        self.__clearTimeShiftCallback()
        CommandMapping.g_instance.onMappingChanged -= self.__onMappingChanged
        super(PreBattleTimer, self)._dispose()

    def __setTimeShitCallback(self):
        self.__callbackID = BigWorld.callback(_TIMER_ANIMATION_SHIFT, self.__updateTimer)

    def __updateTimer(self):
        self.__callbackID = None
        if self.__timeLeft > 0:
            timeLeftWithShift = self.__timeLeft - 1
            self.as_setTimerS(timeLeftWithShift)
        return

    def __clearTimeShiftCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __onMappingChanged(self, *args):
        self.as_setQuestHintS(_ms(PREBATTLE.BATTLEPROGRESS_HINT, hintKey=getReadableKey(CommandMapping.CMD_QUEST_PROGRESS_SHOW)))


class BattleTimer(BattleTimerMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(BattleTimer, self).__init__()
        self.__isTicking = False
        self.__state = COUNTDOWN_STATE.UNDEFINED
        self.__roundLength = self.arenaVisitor.type.getRoundLength()
        self.__endingSoonTime = self.arenaVisitor.type.getBattleEndingSoonTime()
        self.__endWarningIsEnabled = self.__checkEndWarningStatus()
        self.__sounds = dict()

    def destroy(self):
        for sound in self.__sounds.values():
            sound.stop()

        self.__sounds.clear()
        super(BattleTimer, self).destroy()

    @property
    def arenaVisitor(self):
        return self.sessionProvider.arenaVisitor

    def setTotalTime(self, totalTime):
        minutes, seconds = divmod(int(totalTime), 60)
        if self.__endWarningIsEnabled and self.__state == COUNTDOWN_STATE.STOP:
            if _BATTLE_END_TIME < totalTime <= self.__endingSoonTime:
                if not self.__isTicking:
                    self._startTicking()
                if totalTime == self.__endingSoonTime:
                    self._callWWISE(_WWISE_EVENTS.BATTLE_ENDING_SOON)
            elif self.__isTicking:
                self.__stopTicking()
        self._sendTime(minutes, seconds)

    def setState(self, state):
        self.__state = state

    def hideTotalTime(self):
        self.as_showBattleTimerS(False)

    def showTotalTime(self):
        self.as_showBattleTimerS(True)

    def _sendTime(self, minutes, seconds):
        self.as_setTotalTimeS('{:02d}'.format(minutes), '{:02d}'.format(seconds))

    def _callWWISE(self, wwiseEventName):
        sound = SoundGroups.g_instance.getSound2D(wwiseEventName)
        if sound is not None:
            sound.play()
            self.__sounds[wwiseEventName] = sound
        return

    def _setColor(self):
        self.as_setColorS(self.__isTicking)

    def _startTicking(self):
        self._callWWISE(_WWISE_EVENTS.COUNTDOWN_TICKING)
        self.__isTicking = True
        self._setColor()

    def __stopTicking(self):
        self._callWWISE(_WWISE_EVENTS.STOP_TICKING)
        self.__isTicking = False
        self._setColor()

    def __validateEndingSoonTime(self):
        return 0 < self.__endingSoonTime < self.__roundLength

    def __checkEndWarningStatus(self):
        endingSoonTimeIsValid = self.__validateEndingSoonTime()
        return self.arenaVisitor.isBattleEndWarningEnabled() and endingSoonTimeIsValid
