# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/cgf/__init__.py
import CGF
from GenericComponents import EntityGOSync

def getCmpByTypeInTopMostParent(spaceID, gameObject, clazz):
    hierarchy = CGF.HierarchyManager(spaceID)
    rootGameObject = hierarchy.getTopMostParent(gameObject)
    return rootGameObject.findComponentByType(clazz)


def getVehicleFromGO(spaceID, gameObject):
    goSyncComponent = getCmpByTypeInTopMostParent(spaceID, gameObject, EntityGOSync)
    return goSyncComponent.entity if goSyncComponent else None
