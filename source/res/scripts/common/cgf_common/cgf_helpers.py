# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_common/cgf_helpers.py
import typing
import CGF
from constants import IS_EDITOR, IS_CGF_DUMP
if IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle

def getVehicleEntityByGameObject(gameObject):
    return getParentComponentByGameObject(gameObject, Vehicle)


def getVehicleEntityByVehicleGameObject(vehicleGameObject):
    return vehicleGameObject.findComponentByType(Vehicle)


def getVehicleGameObjectByGameObject(gameObject):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, Vehicle)
    return findResult[0] if findResult is not None else None


def getParentComponentByGameObject(gameObject, componentType):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, componentType)
    return findResult[1] if findResult is not None else None


def getParentGameObjectByComponent(gameObject, componentType):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    findResult = hierarchy.findComponentInParent(gameObject, componentType)
    return findResult[0] if findResult is not None else None
