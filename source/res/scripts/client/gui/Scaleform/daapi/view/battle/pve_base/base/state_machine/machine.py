# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/base/state_machine/machine.py
import typing
import BigWorld
from frameworks.state_machine import StateMachine, StateEvent
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.events import OneSecondEvent, ToStateEvent
from gui.Scaleform.daapi.view.battle.pve_base.base.state_machine.states import BaseTimerState
from helpers.CallbackDelayer import CallbackDelayer
STATE_TICK_INTERVAL = 1

class BaseStateMachine(StateMachine):

    def post(self, event):
        if not self.isRunning():
            return
        super(BaseStateMachine, self).post(event)

    def postFinalState(self):
        for state in self.getChildrenStates():
            if state.isFinal():
                super(BaseStateMachine, self).post(ToStateEvent(state.getStateID()))
                return

    def update(self):
        if not self.isRunning():
            return
        for state in self.getChildrenStates():
            if self.isStateEntered(state.getStateID()):
                state.update()


class BaseTimerStateMachine(BaseStateMachine):
    __slots__ = ('_callbackDelayer', '_lastTime')

    def __init__(self):
        super(BaseTimerStateMachine, self).__init__()
        self._callbackDelayer = CallbackDelayer()
        self._lastTime = 0

    def start(self, doValidate=True):
        super(BaseTimerStateMachine, self).start(doValidate)
        self._callbackDelayer.delayCallback(0, self._tick)

    def stop(self):
        self._callbackDelayer.clearCallbacks()
        super(BaseTimerStateMachine, self).stop()

    def _tick(self):
        currentTime = BigWorld.serverTime()
        self.post(OneSecondEvent(lastTime=self._lastTime, currentTime=currentTime))
        for state in self.getChildrenStates():
            if self.isStateEntered(state.getStateID()) and isinstance(state, BaseTimerState):
                state.tick(currentTime)

        self._lastTime = currentTime
        return STATE_TICK_INTERVAL
