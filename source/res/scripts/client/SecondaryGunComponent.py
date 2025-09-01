# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SecondaryGunComponent.py
import typing
import CGF
from vehicles.components.vehicle_component import VehicleGunPrefabDynamicComponent
from vehicles.parts.guns import IGunComponent, createGunShootingEvents
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescriptor
    from vehicles.parts.guns import IGunShootingEvents

class SecondaryGunComponent(VehicleGunPrefabDynamicComponent, IGunComponent):

    def __init__(self):
        super(SecondaryGunComponent, self).__init__()
        self.__shootingEvents = createGunShootingEvents(self.entity, self)
        self._initComponent()

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def getGunInstallationIndex(self):
        return self.gunInstallationIndex

    def getGunRootGameObject(self):
        return self._prefabRoot

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(SecondaryGunComponent, self).onDestroy()

    def onDiscreteShot(self, gunIndex):
        self.__shootingEvents.processDiscreteShot(gunIndex)

    def onMultiShot(self, gunIndexes):
        self.__shootingEvents.processMultiShot(gunIndexes)

    def _getComponentPrefabsSets(self, typeDescriptor):
        return typeDescriptor.gunInstallations[self.getGunInstallationIndex()].gun.prefabs

    def _onAppearanceReady(self):
        super(SecondaryGunComponent, self)._onAppearanceReady()
        self.__shootingEvents.processAppearanceReady()
