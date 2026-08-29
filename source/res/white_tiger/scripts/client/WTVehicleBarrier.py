# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTVehicleBarrier.py
import aih_constants
from AvatarInputHandler import aih_global_binding
from script_component.DynamicScriptComponent import DynamicScriptComponent
_GUN_MARKER_FLAG = aih_constants.GUN_MARKER_FLAG

class WTVehicleBarrier(DynamicScriptComponent):
    gunMarkersFlags = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.GUN_MARKERS_FLAGS)

    def _onAvatarReady(self):
        self.__handleAbilityMode()

    def set_abilityMode(self, prev):
        self.__handleAbilityMode()

    def set_gunLockFlag(self, prev):
        if self.gunLockFlag:
            self.gunMarkersFlags &= ~_GUN_MARKER_FLAG.CLIENT_MODE_ENABLED
            return
        self.gunMarkersFlags |= _GUN_MARKER_FLAG.CLIENT_MODE_ENABLED

    def __handleAbilityMode(self):
        pass
