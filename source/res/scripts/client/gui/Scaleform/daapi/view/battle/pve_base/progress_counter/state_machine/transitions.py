# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/progress_counter/state_machine/transitions.py
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.transitions import ToStateTransition
from pve_battle_hud import ProgressCounterState

class ToAppearanceTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToAppearanceTransition, self).__init__(ProgressCounterState.APPEARANCE, priority=1)


class ToRegularTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToRegularTransition, self).__init__(ProgressCounterState.REGULAR, priority=1)


class ToHiddenTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToHiddenTransition, self).__init__(ProgressCounterState.HIDDEN, priority=0)
