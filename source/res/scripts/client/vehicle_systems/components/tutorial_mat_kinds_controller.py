# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/tutorial_mat_kinds_controller.py
import BigWorld
import material_kinds
import TriggersManager
from svarog_script.py_component import Component
from svarog_script.auto_properties import LinkDescriptor
from helpers.CallbackDelayer import CallbackDelayer
_PERIODIC_TIME = 0.25

class TutorialMatKindsController(Component, CallbackDelayer):
    terrainMatKindsLink = LinkDescriptor()

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__wasOnSoftTerrain = False

    def destroy(self):
        self.deactivate()
        CallbackDelayer.destroy(self)

    def activate(self):
        self.delayCallback(_PERIODIC_TIME, self.__onPeriodicTimer)

    def deactivate(self):
        self.stopCallback(self.__onPeriodicTimer)

    def __onPeriodicTimer(self):
        isOnSoftTerrain = False
        matKinds = self.terrainMatKindsLink()
        for matKind in matKinds:
            if not isOnSoftTerrain:
                groundStr = material_kinds.GROUND_STRENGTHS_BY_IDS.get(matKind)
                isOnSoftTerrain = groundStr == 'soft'

        if self.__wasOnSoftTerrain != isOnSoftTerrain:
            self.__wasOnSoftTerrain = isOnSoftTerrain
            if isOnSoftTerrain:
                TriggersManager.g_manager.activateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_ON_SOFT_TERRAIN)
            else:
                TriggersManager.g_manager.deactivateTrigger(TriggersManager.TRIGGER_TYPE.PLAYER_VEHICLE_ON_SOFT_TERRAIN)
        return _PERIODIC_TIME
