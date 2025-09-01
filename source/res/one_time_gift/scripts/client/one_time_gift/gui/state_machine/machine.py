# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/state_machine/machine.py
from frameworks.state_machine import ConditionTransition, State, StateFlags, StateMachine, StringEventTransition
from one_time_gift.gui.state_machine import state_helpers as helpers, states
from one_time_gift.gui.state_machine.states import OTGEvent, OTGStateID

class OneTimeGiftStateMachine(StateMachine):

    def configure(self, *args, **kwargs):
        root = states.RootState()
        entered = states.EnteredState()
        final = State(OTGStateID.FINAL, StateFlags.SINGULAR | StateFlags.FINAL)
        root.configure()
        entered.configure(root)
        root.addTransition(ConditionTransition(helpers.canReceiveRewards, invert=True, priority=1), target=final)
        root.addTransition(ConditionTransition(lambda _: True), target=root)
        root.wait.addTransition(StringEventTransition(OTGEvent.ENTRY_POINT_CLICK), target=entered)
        root.wait.addTransition(StringEventTransition(OTGEvent.INTRO_START), target=entered.intro)
        entered.addTransition(StringEventTransition(OTGEvent.ERROR, priority=4), target=entered.error)
        entered.addTransition(ConditionTransition(helpers.canReceiveRewards, invert=True, priority=1), target=root)
        self.addState(root)
        self.addState(entered)
        self.addState(final)
