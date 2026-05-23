# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/cgf_helpers.py
import typing
import CGF
from constants import IS_CLIENT
if IS_CLIENT:
    from Vehicle import Vehicle
    from debug_utils import LOG_ERROR

def getVehicleFromGO(vehicleGO, spaceID):
    hierarchyManager = CGF.HierarchyManager(spaceID)
    if hierarchyManager is None:
        LOG_ERROR('unable to extract vehicle, hierarchyManager is None')
        return
    parentGO = hierarchyManager.getTopMostParent(vehicleGO)
    vehicle = parentGO.findComponentByType(Vehicle)
    if not vehicle and vehicle.status < 0:
        LOG_ERROR('unable to extract vehicle component')
        return
    else:
        return vehicle
