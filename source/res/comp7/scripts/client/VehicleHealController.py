# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/VehicleHealController.py
import typing
from helpers import fixed_dict
from script_component.DynamicScriptComponent import DynamicScriptComponent
from view_state_component import ViewStateComponentAdaptor

class VehicleHealController(DynamicScriptComponent):

    def __init__(self):
        super(VehicleHealController, self).__init__()
        self.__adaptors = {}

    def onDestroy(self):
        for adaptor in self.__adaptors.itervalues():
            adaptor.destroy()

        self.__adaptors.clear()
        super(VehicleHealController, self).onDestroy()

    def set_displayedStates(self, prev):
        if self._isAvatarReady:
            self.__invalidateDisplayedStates()

    def _onAvatarReady(self):
        self.__invalidateDisplayedStates()

    def __invalidateDisplayedStates(self):
        removedStates = set(self.__adaptors)
        for stateDict in self.displayedStates:
            state = fixed_dict.getStateWithTimeInterval(stateDict)
            stateID = state.stateID
            if stateID in self.__adaptors:
                self.__adaptors[stateID].updateState(state)
                removedStates.remove(stateID)
            self.__adaptors[stateID] = ViewStateComponentAdaptor(entity=self.entity, state=state)

        for stateID in removedStates:
            adaptor = self.__adaptors.pop(stateID)
            adaptor.destroy()
