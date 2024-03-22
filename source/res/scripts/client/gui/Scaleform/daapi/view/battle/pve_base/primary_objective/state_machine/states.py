# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/primary_objective/state_machine/states.py
import enum
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.states import BaseTimerState, BaseState
from gui.Scaleform.daapi.view.battle.pve_base.pve_helpers import generateText
from pve_battle_hud import PrimaryObjectiveState, getPveHudLogger
_logger = getPveHudLogger()

class TimerState(enum.IntEnum):
    SMALL = 0
    BIG = 1
    NO_TIMER = 2


class InitialState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(InitialState, self).__init__(stateID=PrimaryObjectiveState.INITIAL, flags=StateFlags.INITIAL)


class BaseViewTimerState(BaseTimerState):
    __slots__ = ()

    def tick(self, currentTime):
        super(BaseViewTimerState, self).tick(currentTime)
        serverSettings, _ = self.getSettings()
        finishTime = serverSettings.finishTime
        timeLeft = round(finishTime - currentTime) if finishTime is not None else None
        self._view.updateTimer(timeLeft)
        return

    @property
    def _subheader(self):
        serverSettings, clientSettings = self.getSettings()
        return generateText(clientSettings.subheader, serverSettings.params)


class NoTimerState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(NoTimerState, self).__init__(stateID=PrimaryObjectiveState.NO_TIMER, flags=StateFlags.UNDEFINED)

    @property
    def _subheader(self):
        serverSettings, clientSettings = self.getSettings()
        return generateText(clientSettings.subheader, serverSettings.params)

    def _showView(self):
        super(NoTimerState, self)._showView()
        serverSettings, _ = self.getSettings()
        self._view.as_setTimerStateS(TimerState.NO_TIMER.value)
        self._view.as_setTimerBackgroundS(False)
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)

    def _updateView(self):
        super(NoTimerState, self)._updateView()
        serverSettings, _ = self.getSettings()
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)


class AppearanceState(BaseViewTimerState):
    __slots__ = ()

    def __init__(self):
        super(AppearanceState, self).__init__(stateID=PrimaryObjectiveState.APPEARANCE, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(AppearanceState, self)._showView()
        _, clientSettings = self.getSettings()
        self._view.as_setTimerStateS(TimerState.BIG.value)
        self._view.as_setTimerBackgroundS(True)
        self._view.updateHeaderWithSubheader(clientSettings.header, self._subheader)
        self._view.updateProgress(isVisible=False)
        self._view.playSound(clientSettings.startSound)

    def _updateView(self):
        super(AppearanceState, self)._updateView()
        _, clientSettings = self.getSettings()
        self._view.updateHeaderWithSubheader(clientSettings.header, self._subheader)


class RegularState(BaseViewTimerState):
    __slots__ = ()

    def __init__(self):
        super(RegularState, self).__init__(stateID=PrimaryObjectiveState.REGULAR, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(RegularState, self)._showView()
        serverSettings, _ = self.getSettings()
        self._view.as_setTimerStateS(TimerState.SMALL.value)
        self._view.as_setTimerBackgroundS(False)
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)

    def _updateView(self):
        super(RegularState, self)._updateView()
        serverSettings, _ = self.getSettings()
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)


class RemindState(BaseViewTimerState):
    __slots__ = ()

    def __init__(self, stateID=PrimaryObjectiveState.REMIND, flags=StateFlags.UNDEFINED):
        super(RemindState, self).__init__(stateID=stateID, flags=flags)

    def _showView(self):
        super(RemindState, self)._showView()
        _, clientSettings = self.getSettings()
        self._view.as_setTimerStateS(TimerState.BIG.value)
        self._view.as_playFxS(True, False)
        self._view.as_setTimerBackgroundS(True)
        self._view.updateHeaderWithSubheader(clientSettings.header, self._subheader)
        self._view.updateProgress(isVisible=False)
        self._view.playSound(clientSettings.remindSound)

    def _updateView(self):
        super(RemindState, self)._updateView()
        _, clientSettings = self.getSettings()
        self._view.updateHeaderWithSubheader(clientSettings.header, self._subheader)


class LastRemindState(RemindState):
    __slots__ = ()

    def __init__(self):
        super(LastRemindState, self).__init__(stateID=PrimaryObjectiveState.LAST_REMIND, flags=StateFlags.UNDEFINED)


class LargeTimerState(BaseViewTimerState):
    __slots__ = ()

    def __init__(self):
        super(LargeTimerState, self).__init__(stateID=PrimaryObjectiveState.LARGE_TIMER, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(LargeTimerState, self)._showView()
        serverSettings, _ = self.getSettings()
        self._view.as_setTimerStateS(TimerState.BIG.value)
        self._view.as_setTimerBackgroundS(False)
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)

    def _updateView(self):
        super(LargeTimerState, self)._updateView()
        serverSettings, _ = self.getSettings()
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)


class CountdownState(BaseViewTimerState):
    __slots__ = ()

    def __init__(self):
        super(CountdownState, self).__init__(stateID=PrimaryObjectiveState.COUNTDOWN, flags=StateFlags.UNDEFINED)

    def tick(self, currentTime):
        super(CountdownState, self).tick(currentTime)
        _, clientSettings = self.getSettings()
        self._view.playSound(clientSettings.countdownSound)

    def _showView(self):
        super(CountdownState, self)._showView()
        serverSettings, _ = self.getSettings()
        self._view.as_setTimerStateS(TimerState.BIG.value)
        self._view.as_setTimerBackgroundS(False)
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)
        self._view.as_playFxS(True, True)

    def _updateView(self):
        super(CountdownState, self)._updateView()
        serverSettings, _ = self.getSettings()
        self._view.updateSubheader(self._subheader)
        self._view.updateProgress(serverSettings.progresses)

    def _onExited(self):
        self._view.as_playFxS(False, False)
        super(CountdownState, self)._onExited()


class SuccessState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(SuccessState, self).__init__(stateID=PrimaryObjectiveState.SUCCESS, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(SuccessState, self)._showView()
        _, clientSettings = self.getSettings()
        self._view.hideObjective()
        self._view.showMessage(True, clientSettings.successIcon, clientSettings.success)
        self._view.playSound(clientSettings.successSound)


class FailureState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(FailureState, self).__init__(stateID=PrimaryObjectiveState.FAILURE, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(FailureState, self)._showView()
        _, clientSettings = self.getSettings()
        self._view.hideObjective()
        self._view.showMessage(False, clientSettings.failureIcon, clientSettings.failure)
        self._view.as_setTimerBackgroundS(True)
        self._view.playSound(clientSettings.failureSound)


class HiddenState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(HiddenState, self).__init__(stateID=PrimaryObjectiveState.HIDDEN, flags=StateFlags.FINAL)

    def _showView(self):
        super(HiddenState, self)._showView()
        self._view.hideMessage()
        self._view.hideObjective()
