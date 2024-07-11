# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/races/races_prebattle_timer.py
from account_helpers.settings_core.settings_constants import GRAPHICS
from gui.Scaleform.daapi.view.meta.RacesPrebattleTimerMeta import RacesPrebattleTimerMeta
from gui.battle_control.battle_constants import COUNTDOWN_STATE
from gui.impl.gen import R
from gui.impl import backport
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from races.gui.shared.event import RacesEvent
from skeletons.account_helpers.settings_core import ISettingsCore
_STATE_TO_MESSAGE_RACES = {COUNTDOWN_STATE.WAIT: R.strings.ingame_gui.timer.waiting(),
 COUNTDOWN_STATE.START: R.strings.ingame_gui.timer.starting(),
 COUNTDOWN_STATE.STOP: R.strings.races.battle.timer.start()}

class RacesPreBattleTimer(RacesPrebattleTimerMeta):
    settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('__firstLightEventSent',)

    def __init__(self):
        super(RacesPreBattleTimer, self).__init__()
        self.__firstLightEventSent = False

    def updateBattleCtx(self, battleCtx):
        self._battleTypeStr = battleCtx.getArenaDescriptionString(isInBattle=False)
        if self._state == COUNTDOWN_STATE.WAIT:
            self.as_setWinConditionTextS(self._getMessage())
        else:
            self.as_setWinConditionTextS(backport.text(R.strings.races.battle.timer.caption()))

    def setCountdown(self, state, timeLeft):
        if self._state != state:
            if state == COUNTDOWN_STATE.WAIT:
                self.as_setWinConditionTextS(self._getMessage())
            else:
                self.as_setWinConditionTextS(backport.text(R.strings.races.battle.timer.caption()))
        super(RacesPreBattleTimer, self).setCountdown(state, timeLeft)

    def onFirstLight(self):
        if not self.__firstLightEventSent:
            g_eventBus.handleEvent(RacesEvent(RacesEvent.ON_RACE_FIRST_LIGHTS), scope=EVENT_BUS_SCOPE.BATTLE)
            self.__firstLightEventSent = True

    def onLastLights(self):
        g_eventBus.handleEvent(RacesEvent(RacesEvent.ON_RACE_LAST_LIGHTS), scope=EVENT_BUS_SCOPE.BATTLE)

    def _resetTimer(self):
        self.as_setTimerS(-1)

    def _getStateToMessage(self):
        return _STATE_TO_MESSAGE_RACES

    def _populate(self):
        super(RacesPreBattleTimer, self)._populate()
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
        super(RacesPreBattleTimer, self)._dispose()

    def _updateTimer(self):
        self._clearTimeShiftCallback()
        if self.getTimeLeft >= 0:
            self.as_setTimerS(self.getTimeLeft())
