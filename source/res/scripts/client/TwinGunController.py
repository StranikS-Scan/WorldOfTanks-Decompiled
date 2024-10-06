# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TwinGunController.py
import typing
from vehicle_systems.entity_components.vehicle_mechanic_component import ifAppearanceReady, getVehicleMechanic, getPlayerVehicleMechanic, initOnce, VehicleMechanicGunPrefabComponent
from vehicle_systems.twin_guns.custom_integrations import TwinGunCustomIntegrations
from vehicle_systems.twin_guns.shooting_events import TwinGunShootingEvents
if typing.TYPE_CHECKING:
    from vehicle_systems.twin_guns.system_interfaces import ITwinGunShootingEvents
    from Vehicle import Vehicle

def getVehicleTwinGunController(vehicle):
    return getVehicleMechanic('twinGunController', vehicle)


def getPlayerVehicleTwinGunController():
    return getPlayerVehicleMechanic('twinGunController')


class TwinGunController(VehicleMechanicGunPrefabComponent):

    @initOnce
    def __init__(self):
        super(TwinGunController, self).__init__()
        self.__afterShotDelay = 0.0
        self.__shootingEvents = TwinGunShootingEvents(self)
        TwinGunCustomIntegrations(self.entity, self).subscribe(self.__shootingEvents)
        self._initMechanic()

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def isDoubleBarrelMode(self):
        return len(self.getActiveGunIndexes()) > 1

    def getActiveGunIndexes(self):
        return tuple(self.activeGunIndexes)

    def getAfterShotDelay(self):
        return self.__afterShotDelay

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
        typeDescriptor = self.entity.typeDescriptor
        self.__afterShotDelay = typeDescriptor.gun.twinGun.afterShotDelay
        self.__shootingEvents.processAppearanceReady()
        super(TwinGunController, self)._onAppearanceReady()

    def _onMechanicAppearanceUpdate(self):
        self.__updateActiveGunIndexes()
        self.__updateNextGunIndexes()

    def __updateActiveGunIndexes(self):
        self.__shootingEvents.onActiveGunsUpdate(self.getActiveGunIndexes())

    def __updateNextGunIndexes(self):
        self.__shootingEvents.processNextGunsUpdate(self.getNextGunIndexes())
