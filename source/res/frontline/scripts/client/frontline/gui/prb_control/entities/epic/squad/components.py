# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/prb_control/entities/epic/squad/components.py
from gui.prb_control.entities.base.squad.components import RestrictedRoleTagDataProvider, getRestrictedVehicleClassTag
from items import vehicles

class EpicRestrictedRoleTagDataProvider(RestrictedRoleTagDataProvider):

    def getCurrentVehiclesCount(self, roleTag):
        enableVehicleCount = 0
        unitMgrId, unit = self._unitEntity.getUnit(safe=True)
        if unit is None:
            return enableVehicleCount
        else:
            for slot in self._unitEntity.getSlotsIterator(unitMgrId, unit):
                if slot.player is not None and slot.player.isReady and slot.vehicle is not None:
                    vehType = vehicles.getVehicleType(slot.vehicle.vehTypeCompDescr)
                    if self.getRestrictionLevels(roleTag) and vehType.level not in self.getRestrictionLevels(roleTag):
                        continue
                    vehicleTag = getRestrictedVehicleClassTag(vehType.tags)
                    if roleTag == vehicleTag:
                        enableVehicleCount += 1

            return enableVehicleCount
