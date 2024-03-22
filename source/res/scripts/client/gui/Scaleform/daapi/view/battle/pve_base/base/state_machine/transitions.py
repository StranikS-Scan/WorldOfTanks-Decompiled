# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/base/state_machine/transitions.py
import typing
import BigWorld
from frameworks.state_machine import StringEventTransition, ConditionTransition, StateEvent
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.events import OneSecondEvent
if typing.TYPE_CHECKING:
    from enum import IntEnum
DEFAULT_STATE_DURATION = 4

class ToStateTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, widgetState, priority=3):
        super(ToStateTransition, self).__init__(widgetState.name, priority)


class PostponedTransition(ConditionTransition):
    __slots__ = ('_transitionDelay', '_startCheckTransition')

    def __init__(self, delay=DEFAULT_STATE_DURATION, invert=False, priority=5):
        super(PostponedTransition, self).__init__(self._timerCondition, invert, priority)
        self._transitionDelay = delay
        self._startCheckTransition = None
        return

    def execute(self, event):
        if self._startCheckTransition is None:
            self._startCheckTransition = BigWorld.serverTime()
        isCondition = super(PostponedTransition, self).execute(event)
        if isCondition:
            self._startCheckTransition = None
        return isCondition

    def _timerCondition(self, event):
        return event.currentTime >= self._startCheckTransition + self._transitionDelay if isinstance(event, OneSecondEvent) else False


class BaseTimerCondition(ConditionTransition):

    def __init__(self, invert=False, priority=4):
        super(BaseTimerCondition, self).__init__(self._condition, invert, priority)

    def _condition(self, event, timerValue=0):
        if isinstance(event, OneSecondEvent) and event.lastTime:
            source = self.getSource()
            serverSettings, _ = source.getSettings()
            finishTime = getattr(serverSettings, 'finishTime')
            if finishTime:
                timeLeft = round(finishTime - event.currentTime)
                lastTimeLeft = round(finishTime - event.lastTime)
                return timeLeft <= timerValue <= lastTimeLeft
        return False


class CountdownTimerCondition(BaseTimerCondition):

    def _condition(self, event, timerValue=0):
        if isinstance(event, OneSecondEvent) and event.lastTime:
            source = self.getSource()
            _, clientSettings = source.getSettings()
            countdownTimer = getattr(clientSettings, 'countdownTimer')
            if countdownTimer is not None and countdownTimer > 0:
                return super(CountdownTimerCondition, self)._condition(event, countdownTimer)
        return False


class RegularTimerCondition(ConditionTransition):

    def __init__(self, invert=False, priority=4):
        super(RegularTimerCondition, self).__init__(self._condition, invert, priority)

    def _condition(self, event, *_):
        if isinstance(event, OneSecondEvent):
            source = self.getSource()
            serverSettings, clientSettings = source.getSettings()
            countdownTimer = getattr(clientSettings, 'countdownTimer')
            finishTime = getattr(serverSettings, 'finishTime')
            if finishTime and countdownTimer:
                return finishTime - event.currentTime > countdownTimer
        return False
