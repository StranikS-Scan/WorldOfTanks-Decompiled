# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/progress_counter/state_machine/machine.py
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.machine import BaseStateMachine
from gui.Scaleform.daapi.view.battle.pve_base.progress_counter.state_machine import states
from gui.Scaleform.daapi.view.battle.pve_base.progress_counter.state_machine import transitions

class ProgressCounterStateMachine(BaseStateMachine):

    def configure(self, view, widgetType, widgetId):
        initialState = states.InitialState()
        appearanceState = states.AppearanceState()
        regularState = states.RegularState()
        hiddenState = states.HiddenState()
        initialState.configure(view, widgetType, widgetId)
        appearanceState.configure(view, widgetType, widgetId)
        regularState.configure(view, widgetType, widgetId)
        hiddenState.configure(view, widgetType, widgetId)
        initialState.addTransition(transitions.ToAppearanceTransition(), target=appearanceState)
        initialState.addTransition(transitions.ToRegularTransition(), target=regularState)
        appearanceState.addTransition(transitions.ToRegularTransition(), target=regularState)
        appearanceState.addTransition(transitions.ToHiddenTransition(), target=hiddenState)
        regularState.addTransition(transitions.ToHiddenTransition(), target=hiddenState)
        self.addState(initialState)
        self.addState(appearanceState)
        self.addState(regularState)
        self.addState(hiddenState)
