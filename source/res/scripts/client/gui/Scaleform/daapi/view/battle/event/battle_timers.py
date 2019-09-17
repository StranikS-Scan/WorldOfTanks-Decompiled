# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/battle_timers.py
import SoundGroups
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform.daapi.view.meta.FestivalRacePrebattleTimerMeta import FestivalRacePrebattleTimerMeta
from gui.Scaleform.daapi.view.meta.BattleTimerMeta import BattleTimerMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.impl.gen import R
from gui.impl import backport
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_STATE_TO_MESSAGE_FESTIVAL = {COUNTDOWN_STATE.WAIT: R.strings.ingame_gui.timer.waiting(),
 COUNTDOWN_STATE.START: R.strings.ingame_gui.timer.starting(),
 COUNTDOWN_STATE.STOP: R.strings.festival.festival.timer.started()}

class FestRacePreBattleTimer(FestivalRacePrebattleTimerMeta):
    settingsCore = dependency.descriptor(ISettingsCore)

    def updateBattleCtx(self, battleCtx):
        self._battleTypeStr = battleCtx.getArenaDescriptionString(isInBattle=False)
        if self._state == COUNTDOWN_STATE.WAIT:
            self.as_setWinConditionTextS(self._getMessage())
        else:
            self.as_setWinConditionTextS(backport.text(R.strings.festival.festival.domination.desc()))

    def setCountdown(self, state, timeLeft):
        if self._state != state:
            if state == COUNTDOWN_STATE.WAIT:
                self.as_setWinConditionTextS(self._getMessage())
            else:
                self.as_setWinConditionTextS(backport.text(R.strings.festival.festival.domination.desc()))
        super(FestRacePreBattleTimer, self).setCountdown(state, timeLeft)

    def onFirstLight(self):
        ctrl = self.sessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRaceFirstLights()
        return

    def onLastLights(self):
        ctrl = self.sessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRaceLastLights()
        return

    def _resetTimer(self):
        self.as_setTimerS(-1)

    def _getStateToMessage(self):
        return _STATE_TO_MESSAGE_FESTIVAL

    def _populate(self):
        super(FestRacePreBattleTimer, self)._populate()
        self.settingsCore.onSettingsChanged += self._onSettingsChanged
        isColorBlind = self.settingsCore.getSetting(GRAPHICS.COLOR_BLIND)
        self.__setColorBlindEnabled(isColorBlind)

    def _onSettingsChanged(self, diff):
        if GRAPHICS.COLOR_BLIND in diff:
            isColorBlind = bool(diff[GRAPHICS.COLOR_BLIND])
            self.__setColorBlindEnabled(isColorBlind)

    def __setColorBlindEnabled(self, enabled):
        self.as_setColorBlindS(enabled)

    def _dispose(self):
        self.settingsCore.onSettingsChanged -= self._onSettingsChanged
        super(FestRacePreBattleTimer, self)._dispose()


class _WWISE_EVENTS(object):
    BATTLE_ENDING_SOON = 'time_buzzer_02'
    COUNTDOWN_TICKING = 'time_countdown'
    STOP_TICKING = 'time_countdown_stop'


_BATTLE_END_TIME = 0

class EventBattleTimer(BattleTimerMeta, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventBattleTimer, self).__init__()
        self.__isTicking = False
        self.__state = COUNTDOWN_STATE.UNDEFINED
        self.__roundLength = self.arenaVisitor.type.getRoundLength()
        self.__endingSoonTime = self.arenaVisitor.type.getBattleEndingSoonTime()
        self.__firstBuzzerTime = self.arenaVisitor.type.getBattleEndWarningAppearTime()
        self.__endWarningIsEnabled = self.__checkEndWarningStatus()
        self.__sounds = dict()

    def destroy(self):
        for sound in self.__sounds.values():
            sound.stop()

        self.__sounds.clear()
        super(EventBattleTimer, self).destroy()

    @property
    def arenaVisitor(self):
        return self.sessionProvider.arenaVisitor

    def setTotalTime(self, totalTime):
        minutes, seconds = divmod(int(totalTime), 60)
        if self.__endWarningIsEnabled and self.__state == COUNTDOWN_STATE.STOP:
            if _BATTLE_END_TIME < totalTime <= self.__firstBuzzerTime:
                self.as_setColorS(True)
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

    def __stopTicking(self):
        self._callWWISE(_WWISE_EVENTS.STOP_TICKING)
        self.__isTicking = False
        self._setColor()

    def __validateEndingSoonTime(self):
        return 0 < self.__endingSoonTime < self.__roundLength

    def __checkEndWarningStatus(self):
        endingSoonTimeIsValid = self.__validateEndingSoonTime()
        return self.arenaVisitor.isBattleEndWarningEnabled() and endingSoonTimeIsValid
