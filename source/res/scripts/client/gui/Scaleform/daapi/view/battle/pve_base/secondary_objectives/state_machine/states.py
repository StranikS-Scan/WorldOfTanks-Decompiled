# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/secondary_objectives/state_machine/states.py
from enum import Enum
import BigWorld
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.states import BaseState, BaseTimerState
from pve_battle_hud import SecondaryObjectiveState

class HideType(Enum):
    SUCCESS = 'hideGreen'
    FAILURE = 'hideRed'
    DISAPPEARANCE = 'hide'


class InitialState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(InitialState, self).__init__(stateID=SecondaryObjectiveState.INITIAL, flags=StateFlags.INITIAL)


class BaseViewTimerState(BaseTimerState):

    def tick(self, currentTime):
        super(BaseViewTimerState, self).tick(currentTime)
        serverSettings, _ = self.getSettings()
        timeLeft = round(serverSettings.finishTime - currentTime)
        self._view.updateTimer(serverSettings.id, timeLeft, self._isWarning)

    @property
    def _isWarning(self):
        return False

    def _updateView(self):
        serverSettings, clientSettings = self.getSettings()
        self._view.updateTitle(serverSettings.id, clientSettings.getHeader(serverSettings.params))
        self._view.updateProgress(serverSettings.id, serverSettings.progress)


class AppearanceState(BaseViewTimerState):

    def __init__(self):
        super(AppearanceState, self).__init__(stateID=SecondaryObjectiveState.APPEARANCE, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(AppearanceState, self)._showView()
        serverSettings, clientSettings = self.getSettings()
        self._view.addObjective(serverSettings, clientSettings)
        self._view.playSound(clientSettings.startSound)


class RestoredState(BaseViewTimerState):

    def __init__(self):
        super(RestoredState, self).__init__(stateID=SecondaryObjectiveState.RESTORED, flags=StateFlags.UNDEFINED)

    @property
    def _isWarning(self):
        serverSettings, clientSettings = self.getSettings()
        timeLeft = round(serverSettings.finishTime - BigWorld.serverTime())
        return 0 < timeLeft <= clientSettings.countdownTimer

    def _showView(self):
        super(RestoredState, self)._showView()
        serverSettings, clientSettings = self.getSettings()
        self._view.addObjective(serverSettings, clientSettings)


class RegularState(BaseViewTimerState):

    def __init__(self):
        super(RegularState, self).__init__(stateID=SecondaryObjectiveState.REGULAR, flags=StateFlags.UNDEFINED)


class CountdownState(BaseViewTimerState):

    def __init__(self):
        super(CountdownState, self).__init__(stateID=SecondaryObjectiveState.COUNTDOWN, flags=StateFlags.UNDEFINED)

    @property
    def _isWarning(self):
        return True

    def tick(self, currentTime):
        super(CountdownState, self).tick(currentTime)
        _, clientSettings = self.getSettings()
        self._view.playSound(clientSettings.countdownSound)


class SuccessState(BaseState):

    def __init__(self):
        super(SuccessState, self).__init__(stateID=SecondaryObjectiveState.SUCCESS, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(SuccessState, self)._showView()
        serverSettings, clientSettings = self.getSettings()
        self._view.removeObjective(serverSettings.id, HideType.SUCCESS.value)
        self._view.playSound(clientSettings.successSound)


class FailureState(BaseState):

    def __init__(self):
        super(FailureState, self).__init__(stateID=SecondaryObjectiveState.FAILURE, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(FailureState, self)._showView()
        serverSettings, clientSettings = self.getSettings()
        self._view.removeObjective(serverSettings.id, HideType.FAILURE.value)
        self._view.playSound(clientSettings.failureSound)


class DisappearingState(BaseState):

    def __init__(self):
        super(DisappearingState, self).__init__(stateID=SecondaryObjectiveState.DISAPPEARANCE, flags=StateFlags.UNDEFINED)

    def _showView(self):
        super(DisappearingState, self)._showView()
        serverSettings, _ = self.getSettings()
        self._view.removeObjective(serverSettings.id, HideType.DISAPPEARANCE.value)


class HiddenState(BaseState):

    def __init__(self):
        super(HiddenState, self).__init__(stateID=SecondaryObjectiveState.HIDDEN, flags=StateFlags.FINAL)

    def _showView(self):
        super(HiddenState, self)._showView()
        serverSettings, _ = self.getSettings()
        self._view.removeObjective(serverSettings.id, HideType.DISAPPEARANCE.value)
