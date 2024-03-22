# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/secondary_objectives/state_machine/transitions.py
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.transitions import ToStateTransition
from pve_battle_hud import SecondaryObjectiveState

class ToAppearanceTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToAppearanceTransition, self).__init__(SecondaryObjectiveState.APPEARANCE, priority=2)


class ToRestoredTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToRestoredTransition, self).__init__(SecondaryObjectiveState.RESTORED, priority=2)


class ToRegularTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToRegularTransition, self).__init__(SecondaryObjectiveState.REGULAR, priority=2)


class ToCountdownTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToCountdownTransition, self).__init__(SecondaryObjectiveState.COUNTDOWN, priority=2)


class ToSuccessTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToSuccessTransition, self).__init__(SecondaryObjectiveState.SUCCESS, priority=1)


class ToFailureTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToFailureTransition, self).__init__(SecondaryObjectiveState.FAILURE, priority=1)


class ToDisappearanceTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToDisappearanceTransition, self).__init__(SecondaryObjectiveState.DISAPPEARANCE, priority=1)


class ToHiddenTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToHiddenTransition, self).__init__(SecondaryObjectiveState.HIDDEN, priority=0)
