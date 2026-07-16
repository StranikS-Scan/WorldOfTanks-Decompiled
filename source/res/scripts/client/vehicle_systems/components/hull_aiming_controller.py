# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/hull_aiming_controller.py
import CGF
from cgf_script.registration import registerComponent
from constants import VEHICLE_SIEGE_STATE

@registerComponent
class HullAimingController(object):
    domain = CGF.Domain.ClientEditor
    userVisible = False
    vseVisible = False

    def __init__(self):
        self.__vehicleFilter = None
        self.__vehicleDescriptor = None
        return

    def deactivate(self):
        self.__vehicleFilter = None
        self.__vehicleDescriptor = None
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
            needUpdateSpringsLength = newState == VEHICLE_SIEGE_STATE.ENABLED or newState == VEHICLE_SIEGE_STATE.DISABLED or newState == VEHICLE_SIEGE_STATE.PILLBOX_ENABLED
            physics = self.__vehicleFilter.getVehiclePhysics()
            if physics is None or not needUpdateSpringsLength:
                return
            newSuspensionSpringLength = self.__vehicleDescriptor.chassis.suspensionSpringsLength
            if newSuspensionSpringLength is not None:
                physics.setDamperSpringsLength(newSuspensionSpringLength['left'], newSuspensionSpringLength['right'])
            return


class HullAimingSystem(CGF.System):
    AimingDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactRw(HullAimingController))
    Reactions = CGF.Reactions(AimingDeactivated)

    def update(self):
        for _, aiming in self.reaction(self.AimingDeactivated):
            self.__deactivateAiming(aiming)

    def __deactivateAiming(self, aimingComponent):
        if aimingComponent is not None:
            aimingComponent.deactivate()
        return
