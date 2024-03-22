# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/progress_counter/state_machine/states.py
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.states import BaseState
from gui.Scaleform.daapi.view.battle.pve_base.pve_helpers import generateText
from pve_battle_hud import ProgressCounterState

class InitialState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(InitialState, self).__init__(stateID=ProgressCounterState.INITIAL, flags=StateFlags.INITIAL)


class BaseProgressCounterState(BaseState):

    def _showProgress(self, isAnimated):
        serverSettings, clientSettings = self.getSettings()
        icon = clientSettings.icon
        title = generateText(clientSettings.header, serverSettings.params)
        self._view.as_setDataS(icon, title, isAnimated=isAnimated)

    def _updateView(self):
        self._showProgress(isAnimated=True)


class AppearanceState(BaseProgressCounterState):
    __slots__ = ()

    def __init__(self):
        super(AppearanceState, self).__init__(stateID=ProgressCounterState.APPEARANCE, flags=StateFlags.UNDEFINED)

    def _showView(self):
        self._showProgress(isAnimated=True)


class RegularState(BaseProgressCounterState):
    __slots__ = ()

    def __init__(self):
        super(RegularState, self).__init__(stateID=ProgressCounterState.REGULAR, flags=StateFlags.UNDEFINED)

    def _showView(self):
        self._showProgress(isAnimated=False)


class HiddenState(BaseState):
    __slots__ = ()

    def __init__(self):
        super(HiddenState, self).__init__(stateID=ProgressCounterState.HIDDEN, flags=StateFlags.FINAL)

    def _showView(self):
        self._view.as_setDataS('', '', isAnimated=True)
