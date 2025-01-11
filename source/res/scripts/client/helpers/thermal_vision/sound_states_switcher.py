# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/thermal_vision/sound_states_switcher.py
import SoundGroups

class SoundStatesSwitcher(object):

    def __init__(self, soundGroup, startState, stopState):
        super(SoundStatesSwitcher, self).__init__()
        self.soundGroup = soundGroup
        self.startState = startState
        self.stopState = stopState

    def enable(self):
        SoundGroups.g_instance.setState(self.soundGroup, self.startState)

    def disable(self):
        SoundGroups.g_instance.setState(self.soundGroup, self.stopState)
