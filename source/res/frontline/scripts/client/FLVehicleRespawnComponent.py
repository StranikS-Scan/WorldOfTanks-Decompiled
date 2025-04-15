# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/FLVehicleRespawnComponent.py
import BigWorld
from VehicleRespawnComponent import VehicleRespawnComponent
from constants import IS_VS_EDITOR
from vehicle_systems.stricted_loading import makeCallbackWeak
from items.vehicles import VehicleDescr
if not IS_VS_EDITOR:
    from shared_utils import nextTick

class FLVehicleRespawnComponent(VehicleRespawnComponent):

    def waitForRespawnReadiness(self):
        avatar = BigWorld.player()
        if avatar is None:
            return
        else:
            vehInfo = avatar.arena.vehicles[self.entity.id]
            vehicleType = VehicleDescr(self.entity.publicInfo.compDescr).type
            isCompactDescrUpdated = vehInfo['vehicleType'].type.compactDescr == self.typeCompDescr and vehicleType and vehicleType.compactDescr == self.typeCompDescr
            if not isCompactDescrUpdated:
                nextTick(makeCallbackWeak(self.waitForRespawnReadiness))()
                return
            super(FLVehicleRespawnComponent, self).waitForRespawnReadiness()
            return
