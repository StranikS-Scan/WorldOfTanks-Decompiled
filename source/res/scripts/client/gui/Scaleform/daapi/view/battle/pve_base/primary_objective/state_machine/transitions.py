# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/primary_objective/state_machine/transitions.py
from frameworks.state_machine import StateEvent
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.events import OneSecondEvent
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.transitions import ToStateTransition, BaseTimerCondition
from pve_battle_hud import PrimaryObjectiveState

class ToAppearanceTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToAppearanceTransition, self).__init__(PrimaryObjectiveState.APPEARANCE)


class ToRegularTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToRegularTransition, self).__init__(PrimaryObjectiveState.REGULAR)


class ToRemindTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToRemindTransition, self).__init__(PrimaryObjectiveState.REMIND)


class ToLastRemindTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToLastRemindTransition, self).__init__(PrimaryObjectiveState.LAST_REMIND)


class ToLargeTimerTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToLargeTimerTransition, self).__init__(PrimaryObjectiveState.LARGE_TIMER)


class ToCountdownTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToCountdownTransition, self).__init__(PrimaryObjectiveState.COUNTDOWN, priority=2)


class ToSuccessTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToSuccessTransition, self).__init__(PrimaryObjectiveState.SUCCESS, priority=1)


class ToFailureTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToFailureTransition, self).__init__(PrimaryObjectiveState.FAILURE, priority=1)


class ToHiddenTransition(ToStateTransition):
    __slots__ = ()

    def __init__(self):
        super(ToHiddenTransition, self).__init__(PrimaryObjectiveState.HIDDEN, priority=0)


class RemindTimerCondition(BaseTimerCondition):

    def _condition(self, event, timerValue=0):
        if isinstance(event, OneSecondEvent) and event.lastTime:
            source = self.getSource()
            _, clientSettings = source.getSettings()
            remindTimers = getattr(clientSettings, 'remindTimers')
            if remindTimers:
                for remindTimer in remindTimers[:-1]:
                    result = super(RemindTimerCondition, self)._condition(event, remindTimer)
                    if result:
                        return True

        return False


class LastRemindTimerCondition(BaseTimerCondition):

    def _condition(self, event, timerValue=0):
        if isinstance(event, OneSecondEvent) and event.lastTime:
            source = self.getSource()
            _, clientSettings = source.getSettings()
            remindTimers = getattr(clientSettings, 'remindTimers')
            if remindTimers:
                return super(LastRemindTimerCondition, self)._condition(event, remindTimers[-1])
        return False
