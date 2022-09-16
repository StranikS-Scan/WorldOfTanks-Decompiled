# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/VehicleInspireController.py
import typing
from helpers import fixed_dict
from script_component.DynamicScriptComponent import DynamicScriptComponent
from view_state_component import ViewStateComponentAdaptor

class VehicleInspireController(DynamicScriptComponent):

    def __init__(self):
        super(VehicleInspireController, self).__init__()
        self.__adaptor = None
        return

    def onDestroy(self):
        if self.__adaptor is not None:
            self.__adaptor.destroy()
            self.__adaptor = None
        super(VehicleInspireController, self).onDestroy()
        return

    def set_isActive(self, prev):
        if self._isAvatarReady:
            self.__invalidateDisplayedState()

    def set_displayedState(self, prev):
        if self._isAvatarReady:
            self.__invalidateDisplayedState()

    def _onAvatarReady(self):
        self.__invalidateDisplayedState()

    def __invalidateDisplayedState(self):
        if self.isActive:
            state = fixed_dict.getStateWithTimeInterval(self.displayedState)
            if self.__adaptor is not None:
                self.__adaptor.updateState(state)
            else:
                self.__adaptor = ViewStateComponentAdaptor(entity=self.entity, state=state)
        elif self.__adaptor is not None:
            self.__adaptor.destroy()
            self.__adaptor = None
        return
