# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/prebattle_timers/timer_base.py
import BigWorld
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.PrebattleTimerBaseMeta import PrebattleTimerBaseMeta
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import COUNTDOWN_STATE, BATTLE_CTRL_ID
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from helpers import i18n
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
_TIMER_ANIMATION_SHIFT = 0.4
_STATE_TO_MESSAGE = {COUNTDOWN_STATE.WAIT: R.strings.ingame_gui.timer.waiting(),
 COUNTDOWN_STATE.START: R.strings.ingame_gui.timer.starting(),
 COUNTDOWN_STATE.STOP: R.strings.ingame_gui.timer.started()}

class PreBattleTimerBase(PrebattleTimerBaseMeta, IAbstractPeriodView, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self._state = COUNTDOWN_STATE.WAIT
        self._battleTypeStr = None
        self.__timeLeft = None
        self.__callbackID = None
        self.__arenaPeriod = None
        super(PreBattleTimerBase, self).__init__()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GUI

    def _isDisplayWinCondition(self):
        return True

    def updateBattleCtx(self, battleCtx):
        self._battleTypeStr = battleCtx.getArenaDescriptionString(isInBattle=False)
        self.as_setMessageS(self._getMessage())
        if self._isDisplayWinCondition():
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
        self.as_setMessageS(backport.text(_STATE_TO_MESSAGE[state]))
        self.__clearTimeShiftCallback()
        self.as_hideAllS(speed != 0)

    def _getMessage(self):
        if self._state == COUNTDOWN_STATE.WAIT:
            msg = backport.text(_STATE_TO_MESSAGE[self._state])
        else:
            msg = i18n.makeString(self._battleTypeStr)
        return msg

    def _populate(self):
        super(PreBattleTimerBase, self)._populate()
        self.sessionProvider.addArenaCtrl(self)

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        self.__clearTimeShiftCallback()
        super(PreBattleTimerBase, self)._dispose()

    def __setTimeShitCallback(self):
        self.__callbackID = BigWorld.callback(_TIMER_ANIMATION_SHIFT, self.__updateTimer)

    def __updateTimer(self):
        self.__callbackID = None
        if 0 < self.__timeLeft < 61:
            timeLeftWithShift = self.__timeLeft - 1
            self.as_setTimerS(timeLeftWithShift)
        return

    def __clearTimeShiftCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return
