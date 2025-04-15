# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/SMDetectionDelayObservableComponent.py
from Event import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent
from story_mode_common.story_mode_constants import AwarenessState

class SMDetectionDelayObservableComponent(DynamicScriptComponent):
    onTimersChange = Event()
    onAwarenessStateChanged = Event()

    def __init__(self):
        super(SMDetectionDelayObservableComponent, self).__init__()
        self.timers = {}
        self._state = AwarenessState.NOT_SPOTTED

    def set_timers(self, prevValues):
        self.onTimersChange(prevValues, self.timers)
        if self.timers:
            state = AwarenessState.SPOTTING
        else:
            state = AwarenessState.NOT_SPOTTED
        for key, value in self.timers.iteritems():
            if key not in prevValues:
                if value['spotted']:
                    state = AwarenessState.SPOTTED
            if not prevValues[key]['spotted'] and value['spotted']:
                state = AwarenessState.SPOTTED

        if state != self._state:
            if not (self._state == AwarenessState.SPOTTED and state == AwarenessState.SPOTTING):
                self._state = state
                self.onAwarenessStateChanged(self._state.value)
