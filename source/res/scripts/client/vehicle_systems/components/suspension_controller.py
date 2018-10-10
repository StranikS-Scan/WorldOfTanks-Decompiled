# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/suspension_controller.py
import svarog_script.py_component
from constants import VEHICLE_SIEGE_STATE

class SuspensionController(svarog_script.py_component.Component):

    def __init__(self):
        self.__vehicleFilter = None
        self.__vehicleDescriptor = None
        return

    def deactivate(self):
        self.__vehicleFilter = None
        self.__vehicleDescriptor = None
        super(SuspensionController, self).deactivate()
        return

    def destroy(self):
        self.__vehicleFilter = None
        self.__vehicleDescriptor = None
        return

    def setData(self, vehicleFilter, vehicleDescriptor):
        self.__vehicleFilter = vehicleFilter
        self.__vehicleDescriptor = vehicleDescriptor

    def onSiegeStateChanged(self, newState):
        if self.__vehicleFilter is None or self.__vehicleDescriptor is None:
            return
        else:
            needUpdateSpringsLength = newState == VEHICLE_SIEGE_STATE.ENABLED or newState == VEHICLE_SIEGE_STATE.DISABLED
            physics = self.__vehicleFilter.getVehiclePhysics()
            if physics is None or not needUpdateSpringsLength:
                return
            newSuspensionSpringLength = self.__vehicleDescriptor.chassis.suspensionSpringsLength
            if newSuspensionSpringLength is not None:
                physics.setDamperSpringsLength(newSuspensionSpringLength['left'], newSuspensionSpringLength['right'])
            return
