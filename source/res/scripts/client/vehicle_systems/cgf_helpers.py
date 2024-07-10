# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/cgf_helpers.py
import typing
import CGF
from constants import IS_CLIENT
if IS_CLIENT:
    from Vehicle import Vehicle
else:

    class Vehicle(object):
        pass


def getVehicleEntityByGameObject(gameObject):
    return getVehicleEntityComponentByGameObject(gameObject, Vehicle)


def getVehicleEntityComponentByGameObject(gameObject, componentType):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, componentType)
    return findResult[1] if findResult is not None else None
