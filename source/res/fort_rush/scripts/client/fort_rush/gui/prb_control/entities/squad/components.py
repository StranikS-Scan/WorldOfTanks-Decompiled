# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/prb_control/entities/squad/components.py
from __future__ import absolute_import
import typing
import account_helpers
from gui.prb_control.entities.base.squad.components import SquadRestrictionsProvider
from items.vehicles import getVehicleType
if typing.TYPE_CHECKING:
    from typing import List
    from items.vehicles import VehicleType

class FortRushSquadRestrictionsProvider(SquadRestrictionsProvider):

    def _getAllSelectedVehicles(self, ignoreOwnVehiclesInUnit):
        unitMgrId, unit = self._unitEntity.getUnit(safe=True)
        if unit is None:
            return []
        else:
            ownDbID = account_helpers.getAccountDatabaseID()
            vehicles = []
            for slot in self._unitEntity.getSlotsIterator(unitMgrId, unit):
                if slot.player is not None and slot.player.isReady and slot.vehicle is not None:
                    if ignoreOwnVehiclesInUnit and slot.player.dbID == ownDbID:
                        continue
                    vehicles.append(getVehicleType(slot.vehicle.vehTypeCompDescr))

            return vehicles
