# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TwinGunController.py
import typing
from constants import DEFAULT_GUN_INSTALLATION_INDEX
from vehicles.components.component_wrappers import ifAppearanceReady
from vehicles.components.vehicle_component import VehicleGunPrefabDynamicComponent
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.twin_guns.custom_integrations import TwinGunCustomIntegrations
from vehicles.mechanics.twin_guns.mechanic_events import TwinGunShootingEvents
from vehicles.mechanics.mechanic_helpers import getVehicleMechanic, getPlayerVehicleMechanic
from vehicles.parts.guns import IGunComponent
if typing.TYPE_CHECKING:
    import CGF
    from vehicles.mechanics.twin_guns.mechanic_interfaces import ITwinGunShootingEvents
    from Vehicle import Vehicle

def getVehicleTwinGunController(vehicle):
    return getVehicleMechanic(VehicleMechanic.TWIN_GUN, vehicle)


def getPlayerVehicleTwinGunController():
    return getPlayerVehicleMechanic(VehicleMechanic.TWIN_GUN)


class TwinGunController(VehicleGunPrefabDynamicComponent, IGunComponent):

    def __init__(self):
        super(TwinGunController, self).__init__()
        self.__afterShotDelay = 0.0
        self.__shootingEvents = TwinGunShootingEvents(self)
        TwinGunCustomIntegrations(self.entity, self).subscribe(self.__shootingEvents)
        self._initComponent()

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def isDoubleBarrelMode(self):
        return len(self.getActiveGunIndexes()) > 1

    def getActiveGunIndexes(self):
        return tuple(self.activeGunIndexes)

    def getAfterShotDelay(self):
        return self.__afterShotDelay

    def getGunInstallationIndex(self):
        return DEFAULT_GUN_INSTALLATION_INDEX

    def getGunRootGameObject(self):
        return self._prefabRoot

    def getNextGunIndexes(self):
        return tuple(self.nextGunIndexes or self.activeGunIndexes)

    def getShotsCount(self):
        return self.shotsCount

    @ifAppearanceReady
    def set_activeGunIndexes(self, _=None):
        self.__updateActiveGunIndexes()

    @ifAppearanceReady
    def set_nextGunIndexes(self, _=None):
        self.__updateNextGunIndexes()

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(TwinGunController, self).onDestroy()

    def onDiscreteShot(self, gunIndex):
        self.__shootingEvents.processDiscreteShot(gunIndex)

    def onDoubleShot(self):
        self.__shootingEvents.processDoubleShot()

    def _onAppearanceReady(self):
        super(TwinGunController, self)._onAppearanceReady()
        self.__shootingEvents.processAppearanceReady()

    def _onComponentAppearanceUpdate(self):
        self.__updateActiveGunIndexes()
        self.__updateNextGunIndexes()

    def _collectComponentParams(self, typeDescriptor):
        super(TwinGunController, self)._collectComponentParams(typeDescriptor)
        self.__afterShotDelay = typeDescriptor.gun.twinGun.afterShotDelay

    def __updateActiveGunIndexes(self):
        self.__shootingEvents.onActiveGunsUpdate(self.getActiveGunIndexes())

    def __updateNextGunIndexes(self):
        self.__shootingEvents.processNextGunsUpdate(self.getNextGunIndexes())
